#!/usr/bin/env python3
"""Download a species' MLST scheme from PubMLST and prepare the KMA inputs.

Discovering the scheme and its loci requires parsing the API's JSON, which is
why this runs as a script rather than a shell one-liner: neither the locus list
nor the scheme id can be hardcoded, as both vary between species.

For a species <sp> it writes:
    <sp>_profiles.tsv   ST profile table
    <sp>_loci.txt       one locus per line, in PubMLST order
    <sp>_alelos.fasta   all alleles concatenated, ready for `kma index`
"""

import argparse
import os
import sys

import pubmlst_api as api


def validate_profiles(text, loci, db):
    """Check that the profile table is usable before building the database.

    Requires the scheme's loci to be present as columns. A looser check on the
    header alone matches almost any text, including API error pages.
    """
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) < 2:
        raise RuntimeError(f"Profile table for '{db}' is empty or has no data rows.")

    columns = [c.strip() for c in lines[0].split("\t")]
    if columns[0] != "ST":
        raise RuntimeError(
            f"Profile header for '{db}' does not start with 'ST': {columns[:3]}"
        )

    missing = [l for l in loci if l not in columns]
    if missing:
        raise RuntimeError(
            f"Profile table for '{db}' is missing scheme loci columns: {missing}"
        )
    return len(lines) - 1


def main():
    p = argparse.ArgumentParser(description="Download an MLST scheme from PubMLST for NAKAST.")
    p.add_argument("--species", required=True,
                   help="Species: 'sagalactiae' or 'pubmlst_sagalactiae_seqdef'")
    p.add_argument("--scheme", default=None,
                   help="Force a scheme id. Autodetected by default.")
    p.add_argument("--outdir", default=".", help="Output directory")
    args = p.parse_args()

    db = api.resolve_db(args.species)
    sp = api.short_name(db)
    os.makedirs(args.outdir, exist_ok=True)
    out_path = lambda n: os.path.join(args.outdir, n)

    print(f"[INFO] PubMLST database: {db}")

    scheme = api.detect_mlst_scheme(db, args.scheme)
    scheme_id = scheme["_id"]
    loci = api.scheme_loci(scheme)
    if not loci:
        raise RuntimeError(f"Scheme {scheme_id} of '{db}' declares no loci.")

    print(f"[INFO] MLST scheme detected: id={scheme_id} "
          f"({scheme.get('description','?')}) with {len(loci)} loci: {', '.join(loci)}")

    if not api.has_profiles(scheme):
        raise RuntimeError(
            f"Scheme {scheme_id} of '{db}' defines no ST profiles, "
            f"so no Sequence Type can be assigned."
        )

    # --- ST profiles ---
    profiles = api.get_text(
        f"{api.BASE_URL}/db/{db}/schemes/{scheme_id}/profiles_csv")
    n_profiles = validate_profiles(profiles, loci, db)
    with open(out_path(f"{sp}_profiles.tsv"), "w") as fh:
        fh.write(profiles)
    print(f"[INFO] {n_profiles} ST profiles downloaded.")

    # --- alleles, one request per locus ---
    total = 0
    with open(out_path(f"{sp}_alelos.fasta"), "w") as out:
        for locus in loci:
            fasta = api.get_text(f"{api.BASE_URL}/db/{db}/loci/{locus}/alleles_fasta")
            if not fasta.startswith(">"):
                raise RuntimeError(
                    f"Alleles for '{locus}' are not FASTA (they start with "
                    f"{fasta[:40]!r})."
                )
            n = fasta.count(">")
            total += n
            print(f"[INFO]   {locus}: {n} alleles")
            out.write(fasta if fasta.endswith("\n") else fasta + "\n")

    # Authoritative locus list. parse_kma.py reads it instead of guessing
    # which columns of the profile table are loci.
    with open(out_path(f"{sp}_loci.txt"), "w") as fh:
        fh.write("\n".join(loci) + "\n")

    print(f"[INFO] Total: {total} alleles across {len(loci)} loci for {sp}.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
