#!/usr/bin/env python3
"""Catalogue the PubMLST species that NAKAST supports.

Supported means the seqdef database publishes an MLST scheme with defined ST
profiles (a primary key), which is what the pipeline needs to assign a
Sequence Type.

Two modes:
    --tabla                query PubMLST live and print the catalogue
    --write-catalogue D  regenerate assets/pubmlst_species.tsv and
                           docs/supported_species.md under directory D
"""

import argparse
import concurrent.futures as cf
import os
import sys

import pubmlst_api as api


def inspect_database(item):
    """Return the catalogue record for a database, or None if it has no MLST."""
    db, desc = item
    try:
        scheme = api.detect_mlst_scheme(db)
    except Exception:
        return None
    if not api.has_profiles(scheme):
        return None
    loci = api.scheme_loci(scheme)
    if not loci:
        return None
    # Clonal complex is optional in PubMLST; NAKAST reports '-' when a scheme
    # does not define it. `fields` is a list of URLs whose last path segment is
    # the field name.
    fields = {str(u).rstrip("/").split("/")[-1].strip().lower()
              for u in scheme.get("fields", [])}
    return {
        "species": api.short_name(db),
        "description": desc.replace(" sequence/profile definitions", "").strip(),
        "db": db,
        "scheme_id": scheme["_id"],
        "n_loci": len(loci),
        "loci": ",".join(loci),
        "clonal_complex": "yes" if "clonal_complex" in fields else "no",
    }


def build_catalogue(workers=6):
    databases = api.list_seqdef_databases()
    print(f"[INFO] Querying {len(databases)} PubMLST seqdef databases...", file=sys.stderr)
    rows = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(inspect_database, databases):
            if r:
                rows.append(r)
    rows.sort(key=lambda r: r["description"].lower())
    print(f"[INFO] {len(rows)} supported species out of {len(databases)} databases.", file=sys.stderr)
    return rows


COLUMNS = ["species", "description", "db", "scheme_id", "n_loci", "clonal_complex", "loci"]


def write_tsv(rows, path):
    with open(path, "w") as fh:
        fh.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in COLUMNS) + "\n")


def write_md(rows, path):
    with_cc = sum(1 for r in rows if r["clonal_complex"] == "yes")
    not_seven = sum(1 for r in rows if r["n_loci"] != 7)
    other_scheme = sum(1 for r in rows if r["scheme_id"] != "1")
    with open(path, "w") as fh:
        fh.write("# Species supported by NAKAST\n\n")
        fh.write(
            "Generated automatically by `bin/list_pubmlst_species.py` from the\n"
            "PubMLST REST API (<https://rest.pubmlst.org>).\n\n"
            "A species is supported when its `seqdef` database publishes an MLST\n"
            "scheme with defined ST profiles, which is what NAKAST needs to assign\n"
            "a Sequence Type.\n\n"
        )
        fh.write("## Summary\n\n")
        fh.write(f"- **{len(rows)} supported species**\n")
        fh.write(f"- {with_cc} define a Clonal Complex; the rest report `CC = -`\n")
        fh.write(f"- {not_seven} use a number of loci other than 7\n")
        fh.write(f"- {other_scheme} use a `scheme_id` other than 1 (NAKAST detects it)\n\n")
        fh.write("## Usage\n\n")
        fh.write("The value in the `species` column below is what goes in the\n")
        fh.write("`species` column of the samplesheet:\n\n")
        fh.write("```\nsample_id\tfastq_dir\tspecies\n")
        fh.write("M1\tdata/M1\tsagalactiae\n```\n\n")
        fh.write("To query the list live:\n\n")
        fh.write("```bash\nnextflow run nakast.nf --list_species\n```\n\n")
        fh.write("## Catalogue\n\n")
        fh.write("| Organism | `species` | PubMLST database | Scheme | Loci | CC |\n")
        fh.write("|---|---|---|---:|---:|:-:|\n")
        for r in rows:
            fh.write(f"| {r['description']} | `{r['species']}` | `{r['db']}` | "
                     f"{r['scheme_id']} | {r['n_loci']} | {r['clonal_complex']} |\n")
        fh.write("\n## Loci per scheme\n\n")
        for r in rows:
            fh.write(f"- **`{r['species']}`** ({r['n_loci']}): {r['loci'].replace(',', ', ')}\n")


def main():
    p = argparse.ArgumentParser(description="PubMLST species supported by NAKAST.")
    p.add_argument("--tabla", action="store_true",
                   help="Print the live catalogue to stdout")
    p.add_argument("--write-catalogue", metavar="DIR", default=None,
                   help="Regenerate assets/ and docs/ under the given repository directory")
    args = p.parse_args()

    rows = build_catalogue()

    if args.write_catalogue:
        root = args.write_catalogue
        os.makedirs(os.path.join(root, "assets"), exist_ok=True)
        os.makedirs(os.path.join(root, "docs"), exist_ok=True)
        tsv = os.path.join(root, "assets", "pubmlst_species.tsv")
        md = os.path.join(root, "docs", "supported_species.md")
        write_tsv(rows, tsv)
        write_md(rows, md)
        print(f"[INFO] Wrote {tsv}")
        print(f"[INFO] Wrote {md}")
        return

    # Table mode, used by --list_species
    print(f"{'species':<28} {'scheme':>7} {'loci':>5}  {'CC':<3} organism")
    print("-" * 100)
    for r in rows:
        print(f"{r['species']:<28} {r['scheme_id']:>7} {r['n_loci']:>5}  "
              f"{r['clonal_complex']:<3} {r['description']}")
    print("-" * 100)
    print(f"{len(rows)} supported species. "
          f"Use the value in the 'species' column in your samplesheet.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
