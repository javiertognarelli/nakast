#!/usr/bin/env python3
import sys
import argparse
import pandas as pd
import os

def _resolve(p, basedir):
    """Resolve relative samplesheet paths against basedir.

    The script runs inside Nextflow's work directory, so relative paths must
    be interpreted relative to the launch directory instead.
    """
    p = str(p).strip()
    return p if os.path.isabs(p) else os.path.join(basedir, p)

def load_valid_species(catalogue):
    """Read the 'species' column of assets/pubmlst_species.tsv."""
    if catalogue is None:
        return None
    try:
        df = pd.read_csv(catalogue, sep='\t', dtype=str)
        return set(df['species'].str.strip())
    except Exception as e:
        print(f"[WARN] Could not read the species catalogue ({e}). "
              f"Skipping validation of the 'species' column.", file=sys.stderr)
        return None


def validate_samplesheet(file_path, basedir, valid_species=None):
    errors = []
    
    try:
        df = pd.read_csv(file_path, sep='\t')
    except Exception as e:
        sys.exit(f"CRITICAL: could not read the samplesheet. {e}")

    # 1. Required columns. Extra columns are ignored, so samplesheets written
    # for earlier versions of the pipeline keep working.
    required_cols = ['sample_id', 'fastq_dir', 'species']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        sys.exit(f"ERROR: missing columns in the header: {missing_cols}")

    # Normalise identifiers
    df['sample_id'] = df['sample_id'].astype(str).str.strip()
    df['species'] = df['species'].astype(str).str.strip()

    # 2. sample_id must be present
    if df['sample_id'].eq('nan').any() or df['sample_id'].eq('').any():
         errors.append("Row(s) with an empty 'sample_id'.")
    
    # sample_id names the output files, so it must be unique
    if df['sample_id'].duplicated().any():
        dups = df.loc[df['sample_id'].duplicated(), 'sample_id'].unique()
        errors.append(f"Duplicate sample_id values: {dups}")

    # 3. Per-row checks, iterated so each error names its line
    for index, row in df.iterrows():
        line_num = index + 2  # +2 porque index inicia en 0 y hay header
        pid = row['sample_id']

        # NAKAST processes Oxford Nanopore reads only: each sample points at a
        # directory of FASTQ files, typically a barcode folder.
        f_dir = row['fastq_dir']
        if pd.isna(f_dir) or str(f_dir).strip() == '':
            errors.append(f"[Row {line_num} - {pid}] Missing 'fastq_dir'.")
        elif not os.path.exists(_resolve(f_dir, basedir)):
            errors.append(f"[Row {line_num} - {pid}] fastq_dir does not exist: {f_dir}")

        # Check the species against the catalogue so an unknown value fails in
        # seconds rather than after a partial database download.
        sp = row['species']
        if pd.isna(sp) or str(sp).strip() in ('', 'nan'):
            errors.append(f"[Row {line_num} - {pid}] Missing 'species'. "
                          f"Run --list_species to see the supported values.")
        elif valid_species is not None and str(sp).strip() not in valid_species:
            suggestions = [e for e in sorted(valid_species) if e.startswith(str(sp).strip()[:4])][:5]
            extra = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
            errors.append(f"[Row {line_num} - {pid}] Species '{sp}' is not in the PubMLST "
                          f"catalogue.{extra} Run --list_species for the full list.")

    # 4. Report
    if errors:
        print("----------------------------------------------------------------")
        print("SAMPLESHEET ERRORS DETECTED:")
        for e in errors:
            print(f" - {e}")
        print("----------------------------------------------------------------")
        sys.exit(1) # Report con error para detener Nextflow
    else:
        print(f"Samplesheet OK: {len(df)} samples found.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate the NAKAST samplesheet."
    )
    parser.add_argument("samplesheet", help="Samplesheet file (TSV)")
    parser.add_argument(
        "--basedir",
        default=os.getcwd(),
        help="Directory that relative samplesheet paths resolve against "
             "(default: current directory)",
    )
    parser.add_argument(
        "--catalogue",
        default=None,
        help="TSV of supported PubMLST species (assets/pubmlst_species.tsv). "
             "If omitted, the 'species' column is not validated.",
    )
    args = parser.parse_args()
    validate_samplesheet(args.samplesheet, args.basedir,
                         load_valid_species(args.catalogue))
