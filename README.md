# NAKAST

A Nextflow pipeline for automated Multi Locus Sequence Typing (MLST) from Oxford Nanopore
(ONT) amplicon sequencing.

NAKAST takes raw FASTQ reads and produces a final MLST report: read quality control,
quality filtering, automatic download of the relevant PubMLST scheme, database indexing,
alignment with KMA, allele calling, Sequence Type (ST) assignment and Clonal Complex (CC)
assignment where the scheme defines one.

The pipeline was designed and validated with *Streptococcus agalactiae*, but the species is
a per-sample parameter: it works with any of the **135 MLST schemes published by PubMLST**,
and a single run can mix species. See [`docs/supported_species.md`](docs/supported_species.md)
for the full catalogue.

For concepts, assumptions and limitations, read the **User Manual**, available in
[English](docs/USER_MANUAL.md) and [Spanish](docs/MANUAL_USUARIO.md).

Third-party components and their licences are inventoried in
[`docs/THIRD_PARTY_LICENSES.md`](docs/THIRD_PARTY_LICENSES.md).

---

## Requirements

| Component | Version | Notes |
|---|---|---|
| Nextflow | 25.10 or later | Tested on 25.10.2 and 26.04.6 |
| Conda | any recent | Miniconda / Miniforge |
| Mamba | any recent | Used to build environments faster |
| Internet access | — | PubMLST is queried at runtime |

You do **not** need to install KMA, filtlong, chopper, NanoPlot or MultiQC yourself. Each
process declares its own pinned Conda environment and Nextflow builds them on first run.

## Installation

```bash
git clone https://github.com/javiertognarelli/bio_pipelines.git
cd bio_pipelines/mlst_ont_pipeline
```

Check that the pipeline parses and that Conda is enabled:

```bash
nextflow run nakast.nf --help
nextflow config .          # should show conda { enabled = true; useMamba = true }
```

The first real run builds the Conda environments (a few minutes). They are cached in
`$HOME/.nextflow/conda` and reused afterwards.

## Quick start

### 1. Build a samplesheet

A tab-separated file with a header and three columns.

```
sample_id	fastq_dir	species
SGB11	/data/run1/fastq_pass/barcode01	sagalactiae
SGB12	/data/run1/fastq_pass/barcode02	sagalactiae
SGB13	/data/run1/fastq_pass/barcode03	salmonella
```

- `fastq_dir` points at a **directory** of `.fastq.gz` or `.fastq` files (an ONT barcode
  folder). They are concatenated automatically.
- `species` uses the short name from the catalogue. Run `--list_species` to see them all.

Extra columns are ignored, so samplesheets from earlier versions still work.

Relative paths are resolved against the directory you launch from.

### 2. Run

```bash
nextflow run nakast.nf \
    --samplesheet samplesheet.tsv \
    --outdir results
```

Conda is enabled by default, so no `-profile` flag is needed.

### 3. Read the results

```
results/
├── mlst_profiles_<species>.txt      # final MLST report, tab-separated
├── mlst_profiles_<species>.xlsx     # same report as a spreadsheet
├── qc/
│   ├── qc_<sample>/                 # per-sample NanoPlot output
│   └── multiqc_report.html          # aggregated QC
├── consensus_sequences/
│   └── <sample>.fsa                 # KMA consensus per locus
├── reports/
│   ├── <sample>.res                 # raw KMA alignment results
│   └── <species>_profiles.tsv       # PubMLST profile table used for this run
└── pipeline_info/                   # execution report, timeline and trace
```

One report is produced **per species**, because different schemes have different loci and
cannot share a table.

Example report:

```
Sample   ST   CC     adhP  pheS  atr  glnA  sdhA  glcK  tkt  Profile
SGB11    10   cc12   9     1     4    1     3     3     2    OK
SGB12    24   cc452  5     4     4    3     2     3     3    OK
SGB20    -    -      ~9    1     4    1     3     3     2    OK
```

Allele values carry a quality annotation: `9` is an exact match, `~9` has imperfect
identity, `9?` is length-discrepant, `INS` indicates an insertion and `-` means the locus
could not be called confidently. Only profiles made entirely of exact alleles can match a
PubMLST profile and receive an ST. The manual explains the notation in detail.

## Other run modes

```bash
# List the PubMLST species this pipeline can handle (queries PubMLST live)
nextflow run nakast.nf --list_species

# Quality control only: no database download, no typing
nextflow run nakast.nf --samplesheet samplesheet.tsv --qc_only

# Full option list
nextflow run nakast.nf --help
```

## Common parameters

| Parameter | Default | Description |
|---|---|---|
| `--samplesheet` | `samplesheet.tsv` | Input sample table |
| `--outdir` | `results` | Base output directory |
| `--min_depth` | `30` | Minimum depth to call an allele |
| `--min_identity` | `90` | Minimum identity (%) |
| `--allele_coverage` | `90` | Minimum allele coverage (%) |
| `--nano_base_quality` | `20` | Minimum Phred quality for read filtering |
| `--min_length` | `300` | Minimum read length |
| `--keep_percent` | `80` | Keep this percentage of the best reads |
| `--kma_k` | `31` | K-mer size for the KMA index |
| `--generate_consensus` | `true` | Write per-locus consensus sequences |
| `--mlst_report` | `mlst_profiles` | Base name of the final report |

## Resuming an interrupted run

If the PubMLST download fails (network outage), the pipeline retries three times and then
stops, letting the QC steps finish. Once connectivity is back:

```bash
nextflow run nakast.nf --samplesheet samplesheet.tsv --outdir results -resume
```

Everything already completed is reused; only the download and the downstream typing steps
re-run.

## Running without Conda

If you prefer to manage tools yourself, the `host` profile disables Conda and uses whatever
is on `PATH`:

```bash
nextflow run nakast.nf -profile host --samplesheet samplesheet.tsv
```

You then need `kma`, `filtlong`, `chopper`, `NanoPlot`, `multiqc`, and Python with `pandas`,
`numpy` and `openpyxl` available. This is not the recommended mode: it gives up the
reproducibility that the pinned environments provide.

## Citation and authorship

NAKAST — Javier Tognarelli, Genómica UV.
Commissioned by ISP (Daniel Escobar, Fernando Amaya). Panel designed in-house, ISP 2025.

Allele and profile definitions come from PubMLST (<https://pubmlst.org>). If you publish
results produced with this pipeline, cite PubMLST and the relevant scheme alongside the
underlying tools: KMA, filtlong, chopper, NanoPlot and MultiQC.
