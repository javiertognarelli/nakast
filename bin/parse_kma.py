#!/usr/bin/env python3
import os
import glob
import pandas as pd
import numpy as np
import argparse

# Default thresholds; all are overridable from the command line.
MIN_DEPTH = 30.0       # Minimum depth before an allele call is trusted
MIN_IDENTITY = 90.0    # Minimum identity to the reference allele (%)
MIN_COVERAGE = 90.0    # Minimum template coverage (%)

# The number of loci is not a constant: PubMLST schemes carry between 2 and 10.
# The list comes from <species>_loci.txt, written by download_pubmlst.py from
# the scheme definition itself.

def load_loci(path):
    with open(path) as fh:
        loci = [l.strip() for l in fh if l.strip()]
    if not loci:
        raise ValueError(f"Locus file '{path}' is empty.")
    return loci


def order_loci(loci, db_df):
    """Order loci as they appear in the profile table.

    That is PubMLST's canonical order, so the report columns match the official
    scheme table.
    """
    if db_df is None:
        return list(loci)
    present = set(loci)
    in_table = [c for c in db_df.columns if c in present]
    return in_table + [l for l in loci if l not in in_table]


def split_locus_allele(template):
    """Split '<locus>_<number>' into (locus, number).

    Splits from the RIGHT: several PubMLST loci contain underscores in their
    name ('MLST_adk_1', '16S_rRNA_1', 'int_hyp_1'). Splitting from the left
    yields 'MLST', '16S' or 'int' as the locus and corrupts the profile
    without raising an error.
    """
    for sep in ("_", "-"):
        if sep in template:
            locus, _, allele = template.rpartition(sep)
            if allele.isdigit():
                return locus, allele
    return template, ""


def process_sample(filepath, loci, depth_threshold=MIN_DEPTH, min_identity=MIN_IDENTITY, min_coverage=MIN_COVERAGE):
    sample_name = os.path.basename(filepath).replace(".res", "")

    # KMA .res files are tab-separated with a header row.
    try:
        df = pd.read_csv(filepath, sep="\t")
    except Exception as e:
        print(f"[ERROR] Could not read {filepath}: {e}")
        return

    # KMA pads its column names with spaces
    df.columns = df.columns.str.strip()

    # Discard templates with no meaningful support
    df_clean = df[ (df['Depth'] >= depth_threshold) ].copy()

    # Split the template id into locus and allele number: 'glcK_172' becomes
    # ('glcK', '172'). See split_locus_allele().
    split_ids = df_clean['#Template'].apply(split_locus_allele)
    df_clean['Locus'] = split_ids.apply(lambda t: t[0])
    df_clean['Allele'] = split_ids.apply(lambda t: t[1])

    # Pick one winning allele per locus
    winners = annotate_alleles(df_clean, min_identity, min_coverage, min_depth=depth_threshold)

    # A profile is complete only if every locus of the scheme was recovered
    loci_found = len(winners)

    loci_expected = len(loci)

    status = "OK"
    if loci_found < loci_expected:
        status = f"INCOMPLETE ({loci_found}/{loci_expected})"

    # Order the loci as PubMLST publishes them. pd.Categorical turns any locus
    # outside `loci` into NaN, so `loci` must belong to this species' scheme.
    winners['Locus'] = pd.Categorical(winners["Locus"], categories=loci, ordered=True)

    # Transpose into a single profile row: one column per locus
    winners = winners.sort_values("Locus").set_index("Locus")
    profile = winners[['Allele']].T
    profile.insert(0, 'Sample', sample_name)
    profile["Profile"] = status

    return profile

def annotate_alleles(df, min_identity=MIN_IDENTITY, min_coverage=MIN_COVERAGE, min_depth=30, perfect_bonus=1.5):

    df = df.copy()
    df["Allele"] = df["Allele"].astype(str)

    # Depth filter first, before any ranking
    df = df[df["Depth"] >= min_depth].copy()

    # Normalised alignment metrics
    df["Score_Ratio"]    = df["Score"] / df["Expected"]
    df["Score_per_depth"] = df["Score"] / (df["Depth"] * df["Template_length"])

    # A perfect match gets a multiplicative bonus rather than an absolute
    # override, so it still needs depth behind it to win the locus.
    df["_is_perfect"] = (
        (df["Template_Identity"] == 100) &
        (df["Template_Coverage"] == 100) &
        (df["Query_Coverage"]    == 100)
    ).astype(int)

    df["Confidence"] = (
        df["Score_Ratio"] 
        * np.log1p(df["Depth"])
        * (1 + df["_is_perfect"] * (perfect_bonus - 1))  # ej: 1.5x si es perfecto
    )

    # Confidence alone decides the winner
    df = (
        df.sort_values(
            by=["Locus", "Confidence"],
            ascending=[True, False]
        )
        .drop_duplicates(subset="Locus", keep="first")
        .drop(columns="_is_perfect")
        .copy()
    )

    exact_ident = df["Template_Identity"] == 100
    exact_tcov  = df["Template_Coverage"] == 100
    qcov_exact  = df["Query_Coverage"] == 100
    qcov_ins    = df["Query_Coverage"] <  100
    qcov_trunc  = df["Query_Coverage"] >  100
    good_ident  = df["Template_Identity"] >= min_identity
    good_tcov   = df["Template_Coverage"] >= min_coverage

    df["Allele"] = np.select(
        [
            qcov_ins,
            qcov_exact & exact_ident & exact_tcov,
            qcov_exact & ~exact_ident & exact_tcov,
            qcov_trunc & good_ident & good_tcov,
            ~good_ident | ~good_tcov,
        ],
        [
            "INS",
            df["Allele"],
            "~" + df["Allele"],
            df["Allele"] + "?",
            "-",
        ],
        default="-"
    )

    return df

def assign_st(df, db_df, genes):
    """Assign ST and CC by matching the allelic signature against PubMLST.

    `genes` is the scheme's locus list and `db_df` the profile table already
    loaded with dtype=str (see read_profiles). The match is exact: an annotated
    allele such as '~9' matches no profile, which is intended.
    """
    if db_df is None:
        print("[INFO] No MLST profile table supplied; skipping ST assignment.")
        df.insert(1, 'ST', '-')
        df.insert(2, 'CC', '-')
        return df

    missing_in_table = [g for g in genes if g not in db_df.columns]
    if missing_in_table:
        print(f"[ERROR] The profile table has no columns for loci {missing_in_table}. "
              f"Skipping ST assignment.")
        df.insert(1, 'ST', '-')
        df.insert(2, 'CC', '-')
        return df

    db_df = db_df.copy()
    db_df["signature"] = db_df[genes].fillna("-").astype(str).agg("/".join, axis=1)

    missing_genes = [g for g in genes if g not in df.columns]
    if missing_genes:
        df = df.copy()
        df[missing_genes] = "-"
    df["signature"] = df[genes].astype(str).agg("/".join, axis=1)
    
    # Detect the clonal complex column across naming variants
    cc_aliases = {"clonal_complex", "clonal complex", "cc", "clonalcomplex"}
    cc_col = next((c for c in db_df.columns if c.strip().lower() in cc_aliases), None)
    cols = ["ST", "signature"] + ([cc_col] if cc_col else [])

    out = df.merge(db_df[cols], on="signature", how="left")

    out["ST"] = out["ST"].apply(lambda x: str(int(x)) if pd.notna(x) and x != "-" else "-") # drop decimals from ST and fill unmatched rows with '-'

    if cc_col:
        out = out.rename(columns={cc_col: "CC"})
        out["CC"] = out["CC"].fillna("-")
    else:
        out["CC"] = "-"

    order = ["Sample", "ST", "CC"] + list(genes) + ["Profile"]

    order = [c for c in order if c in out.columns]
    return out[order].replace("", pd.NA).fillna("-")

def read_profiles(path):
    """Read the PubMLST profile table.

    dtype=str matters: with a blank cell anywhere in a locus column pandas
    would infer floats, the signature would read '1.0/1/2/...', and every
    profile match would fail silently, returning ST='-' for all samples.
    """
    if path is None:
        return None
    try:
        return pd.read_csv(path, sep="\t", dtype=str)
    except Exception as e:
        print(f"[ERROR] Could not read the MLST profile table: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Call MLST alleles from KMA results.")
    parser.add_argument("-i","--input_folder", help="Directory containing .res files", required=True)
    parser.add_argument("-p","--profiles", required=False, help="PubMLST profile table (TSV)")
    parser.add_argument("-l","--loci", required=False,
                        help="File with one locus per line (<species>_loci.txt). "
                             "If omitted, loci are inferred from the profile table.")
    parser.add_argument("-o","--output", default="mlst_perfiles", help="Base name for the .txt and .xlsx reports")
    parser.add_argument("-d","--min_depth", type=int, default=MIN_DEPTH, help="Minimum depth to consider an allele")
    parser.add_argument("--min_identity", type=float, default=MIN_IDENTITY, help="Minimum identity to consider an allele")
    parser.add_argument("-c","--min_coverage", type=float, default=MIN_COVERAGE, help="Minimum coverage to consider an allele")
    args = parser.parse_args()

    db_df = read_profiles(args.profiles)

    # Locus list. Preferred source is the file written by download_pubmlst.py.
    # Failing that, infer it from the profile table by dropping ST and the
    # metadata columns PubMLST may append (clonal_complex, species, ...).
    if args.loci:
        loci = load_loci(args.loci)
    elif db_df is not None:
        non_locus = {"st", "clonal_complex", "species", "mlst_clade", "lineage", ""}
        loci = [c for c in db_df.columns if c.strip().lower() not in non_locus]
    else:
        parser.error("Either --loci or --profiles is required to know the scheme loci.")

    loci = order_loci(loci, db_df)
    print(f"[INFO] Scheme with {len(loci)} loci: {', '.join(loci)}")

    # One .res file per sample
    files = sorted(glob.glob(os.path.join(args.input_folder, "*.res")))

    profiles = []

    for f in files:
        profile = process_sample(f, loci, depth_threshold=args.min_depth, min_identity=args.min_identity, min_coverage=args.min_coverage)
        if profile is not None and not profile.empty:
            profiles.append(profile)

    if not profiles and args.input_folder:
        # Both formats are written even when empty: GENERATE_REPORT declares
        # .txt and .xlsx as outputs and fails if either is missing.
        empty = pd.DataFrame(columns=["Sample", "ST", "CC"] + list(loci) + ["Profile"])
        empty.to_csv(f"{args.output}.txt", sep="\t", index=False)
        empty.to_excel(f"{args.output}.xlsx", index=False)
        print(f"[INFO] No MLST profiles generated. Empty reports written to {args.output}.*")
        return

    profiles_df = pd.concat(profiles, ignore_index=True)
    st_cc_asign_df = assign_st(profiles_df, db_df, loci)

    st_cc_asign_df.sort_values(by='Sample').to_csv(f"{args.output}.txt", sep="\t", index=False)
    st_cc_asign_df.sort_values(by='Sample').to_excel(f"{args.output}.xlsx", index=False)
    print(f"[INFO] MLST profiles written to {args.output}")

if __name__ == "__main__":
    main()
