# NAKAST — User Manual

Detailed reference for the NAKAST MLST pipeline. For installation and a first run, see the
[README](../README.md).

## Contents

1. [What NAKAST does](#1-what-nakast-does)
2. [Background concepts](#2-background-concepts)
3. [Workflow architecture](#3-workflow-architecture)
4. [Input specification](#4-input-specification)
5. [Parameter reference](#5-parameter-reference)
6. [Output reference](#6-output-reference)
7. [How allele calling works](#7-how-allele-calling-works)
8. [ST and CC assignment](#8-st-and-cc-assignment)
9. [Species support](#9-species-support)
10. [Assumptions](#10-assumptions)
11. [Limitations](#11-limitations)
12. [Parameter tuning notes](#12-parameter-tuning-notes)
13. [Troubleshooting](#13-troubleshooting)
14. [Reproducibility](#14-reproducibility)

---

## 1. What NAKAST does

NAKAST determines MLST profiles from ONT amplicon reads in a single reproducible flow:

```
FASTQ (barcode dir)
   └─> concatenate
        └─> quality/length filtering (filtlong + chopper)
             ├─> read QC (NanoPlot -> MultiQC)
             └─> align against the PubMLST allele database (KMA)
                  └─> allele calling, ST and CC assignment -> report (.txt + .xlsx)

PubMLST REST API
   └─> scheme detection -> allele download -> KMA index
```

Everything between raw reads and the final table is automated, including fetching and
indexing the reference database.

## 2. Background concepts

**MLST (Multi Locus Sequence Typing)** characterises a bacterial isolate by sequencing a
small set of housekeeping gene fragments, usually seven. Each distinct sequence at a locus
gets an integer **allele number**, curated centrally.

**Allelic profile** is the ordered set of allele numbers, for example `9-1-4-1-3-3-2`.

**Sequence Type (ST)** is an integer assigned to each distinct allelic profile. A profile
matches an ST only if *every* allele is an exact match to a known allele. A single
uncharacterised locus leaves the isolate untyped.

**Clonal Complex (CC)** groups related STs that share most of their alleles. Not every
scheme defines clonal complexes. In this catalogue, 102 of 135 schemes do; the rest report
`CC = -`, which is correct rather than a failure.

**PubMLST** (<https://pubmlst.org>) hosts the reference allele sequences and profile tables.
NAKAST queries its REST API directly, so results always reflect the current state of the
database.

**KMA** is the aligner used here. It maps reads against a k-mer indexed database of allele
sequences and reports, per template, identity, coverage and depth. It is well suited to
redundant amplicon data because it resolves which of many near-identical alleles best
explains the reads.

## 3. Workflow architecture

| Process | Tool | Purpose |
|---|---|---|
| `VALIDATE_SAMPLESHEET` | python, pandas | Pre-flight check of the samplesheet |
| `DOWNLOAD_PREP_DB` | python, kma | Detect scheme, download alleles/profiles, build index |
| `concat_ONT_fastq` | coreutils, gzip | Merge a barcode directory into one FASTQ |
| `FILTER_ONT` | filtlong, chopper | Length and quality filtering |
| `NANOPLOT` | NanoPlot | Per-sample read QC |
| `MULTIQC` | MultiQC | Aggregate QC report |
| `KMA_RUN` | kma | Align reads against the allele database |
| `GENERATE_REPORT` | python, pandas, openpyxl | Allele calling, ST/CC assignment, reports |
| `LIST_SPECIES` | python | Print the compatible-species catalogue |

**Species is a grouping key.** `DOWNLOAD_PREP_DB` runs once per distinct species in the
samplesheet; each sample is joined to the database of its own species; and one report is
emitted per species. Mixed-species batches are therefore a normal case, not a workaround.

**Failure behaviour** differs by stage, on purpose:

| Process | Strategy | Rationale |
|---|---|---|
| `VALIDATE_SAMPLESHEET` | `terminate` | A bad samplesheet should stop everything immediately |
| `DOWNLOAD_PREP_DB` | retry ×3, then `finish` | Survives transient network failures; lets QC finish, then stops so `-resume` can continue |
| `KMA_RUN`, `GENERATE_REPORT` | `terminate` | A silent failure here would produce a run with no results and exit 0 |
| `concat_ONT_fastq`, `FILTER_ONT`, `NANOPLOT`, `MULTIQC` | `ignore` | One bad sample should not abort the batch |

## 4. Input specification

A tab-separated file with a header row and three columns.

| Column | Required | Description |
|---|---|---|
| `sample_id` | yes | Unique identifier. Becomes the output file prefix |
| `fastq_dir` | yes | Directory containing `.fastq.gz` or `.fastq` files |
| `species` | yes | Short name from the catalogue, e.g. `sagalactiae` |

Additional columns are ignored, so samplesheets written for earlier versions keep working.

Validation runs before any heavy work and checks that the three columns exist, `sample_id`
is non-empty and unique, the referenced directories exist on disk, and `species` is present
in `assets/pubmlst_species.tsv`. A misspelled species fails in seconds with a suggestion
rather than after a partial download.

Relative paths are resolved against the launch directory. Absolute paths are safer when the
samplesheet is shared between machines.

## 5. Parameter reference

### Input/output

| Parameter | Default | Description |
|---|---|---|
| `--samplesheet` | `samplesheet.tsv` | Input table |
| `--outdir` | `results` | Base output directory |
| `--qc_outdir` | `<outdir>/qc` | QC outputs |
| `--consensus_outdir` | `<outdir>/consensus_sequences` | Consensus FASTA |
| `--report_outdir` | `<outdir>/reports` | `.res` files and profile tables |
| `--mlst_report` | `mlst_profiles` | Base name of the final report |

### Read filtering

| Parameter | Default | Description |
|---|---|---|
| `--nano_base_quality` | `20` | Minimum Phred quality, passed to chopper |
| `--min_length` | `300` | Minimum read length (filtlong) |
| `--keep_percent` | `80` | Keep this percentage of the best reads by bases (filtlong) |

### Allele calling

| Parameter | Default | Description |
|---|---|---|
| `--min_depth` | `30` | Minimum depth, applied both in KMA and in the report script |
| `--min_identity` | `90` | Minimum identity to the reference allele (%) |
| `--allele_coverage` | `90` | Minimum allele (template) coverage (%) |
| `--kma_k` | `31` | K-mer size for the KMA index |
| `--generate_consensus` | `true` | Publish per-locus consensus sequences |

### Modes

| Parameter | Default | Description |
|---|---|---|
| `--qc_only` | `false` | Run QC only; no download, no typing |
| `--list_species` | `false` | Print the compatible-species catalogue and exit |
| `--help` | `false` | Print usage and exit |

### Resources

Resources are assigned by label in `nextflow.config`:

| Label | CPUs | Memory | Time | Processes |
|---|---:|---:|---:|---|
| `process_low` | 2 | 4 GB | 2 h | validation, database, species listing |
| `process_medium` | 6 | 10 GB | 8 h | concatenation, filtering, QC, report |
| `process_high` | 12 | 16 GB | 24 h | KMA alignment |

## 6. Output reference

### Final report

`<outdir>/mlst_profiles_<species>.txt` and `.xlsx`, with one row per sample:

| Column | Content |
|---|---|
| `Sample` | Sample identifier |
| `ST` | Sequence Type, or `-` if the profile matches nothing |
| `CC` | Clonal Complex, or `-` if unassigned or not defined by the scheme |
| one column per locus | Allele call with its quality annotation |
| `Profile` | `OK`, or `INCOMPLETE (n/N)` when fewer than N loci were recovered |

### Intermediate files

- `reports/<sample>.res` — raw KMA output. The authoritative record of identity, coverage,
  depth and score for every template considered. Worth inspecting whenever a call surprises
  you.
- `reports/<species>_profiles.tsv` — the exact PubMLST profile table used for this run.
  Keep it: PubMLST changes over time, and this file makes a run reproducible after the fact.
- `consensus_sequences/<sample>.fsa` — KMA consensus per locus, useful for submitting novel
  alleles or for Sanger confirmation.
- `qc/multiqc_report.html` — aggregated read QC.
- `pipeline_info/` — execution report, timeline and trace.

## 7. How allele calling works

### Step 1 — depth filter

Templates below `--min_depth` are discarded, both by KMA and again in the report script.

### Step 2 — pick a winner per locus

Several alleles of the same locus usually attract reads, since they differ by a few bases.
NAKAST ranks them with a confidence score:

```
Score_Ratio = Score / Expected
Confidence  = Score_Ratio × log1p(Depth) × perfect_bonus
```

where `perfect_bonus` is 1.5 when identity, template coverage and query coverage are all
100%, and 1.0 otherwise. The highest-confidence template wins the locus.

The bonus is multiplicative rather than absolute on purpose: a perfect match still has to be
supported by depth to win, so a single well-aligned read cannot outrank a deeply covered
allele.

### Step 3 — annotate the call

| Notation | Meaning | Condition |
|---|---|---|
| `9` | Exact match | Identity, template coverage and query coverage all 100% |
| `~9` | Imperfect identity | Query coverage 100%, template coverage 100%, identity below 100% |
| `9?` | Length discrepancy | Query coverage above 100% and identity/coverage above thresholds |
| `INS` | Insertion | Query coverage below 100% |
| `-` | Not callable | Identity or template coverage below thresholds, or no template passed |

Only bare integers can match a PubMLST profile. Any annotated allele makes the profile
unmatchable, which is why `ST = -` usually traces back to one annotated locus rather than
to a failure of the ST lookup.

A caveat on `?`: query coverage above 100% means the read is *longer* than the template.
With this amplicon panel that reflects read-through rather than truncation, so the label is
conservative but its wording is imprecise.

## 8. ST and CC assignment

The allele calls are joined into a signature (`9/1/4/1/3/3/2`) and matched against the same
signature built from the PubMLST profile table. The match is exact and string-based:

- Loci are taken from `<species>_loci.txt`, written from the scheme definition, then ordered
  as they appear in the profile table so the report preserves PubMLST's canonical order.
- The profile table is read with `dtype=str` so that a missing value cannot silently turn a
  locus column into floats and produce `1.0/1/2/...`, which would fail every match.
- The CC column is detected tolerantly (`clonal_complex`, `clonal complex`, `cc`,
  `clonalcomplex`). When absent, `CC = -`.
- No match returns `ST = -`. NAKAST never reports a nearest or approximate ST.

## 9. Species support

`assets/pubmlst_species.tsv` and `docs/supported_species.md` catalogue the **135
PubMLST schemes** that define ST profiles. Regenerate them with:

```bash
python3 bin/list_pubmlst_species.py --write-catalogue .
```

Two assumptions that hold for *S. agalactiae* but not in general, and which NAKAST therefore
handles dynamically:

- **The MLST scheme is not always scheme 1.** Seven schemes use a different id; *Salmonella*
  uses 2. NAKAST finds the scheme whose description starts with `MLST` instead of assuming.
- **Schemes do not always have seven loci.** They range from 2 to 10; 48 of 135 differ from
  seven. The locus list comes from the scheme definition, never from a hardcoded list.

Locus names are also less regular than they look: `MLST_adk`, `16S_rRNA` and `int_hyp` all
contain underscores, so allele identifiers are split from the right.

## 10. Assumptions

Understanding these matters for interpreting results.

1. **Amplicon sequencing, not whole genome.** The pipeline assumes reads come from targeted
   amplification of the MLST loci. Depth is expected in the hundreds or thousands, and the
   default thresholds reflect that. Running WGS data through it will produce far lower
   per-locus depth and many `-` calls.
2. **The species is known and declared.** NAKAST does not identify the organism. It types
   the sample against the scheme you specify. A wrong `species` produces a confidently wrong
   or empty result, not an error.
3. **PubMLST is reachable and authoritative.** The database is downloaded fresh on every
   run. Results depend on the state of PubMLST at run time, which is why the profile table
   is published with the outputs.
4. **The scheme defines ST profiles.** Schemes without a primary key (cgMLST and similar)
   are excluded from the catalogue and rejected at download time.
5. **Sample identifiers are unique** across the samplesheet. They name the output files.
6. **Reads are basecalled and demultiplexed.** NAKAST starts from per-barcode FASTQ; it does
   not basecall, demultiplex, or trim adapters and barcodes.
7. **One species per sample.** Mixed or contaminated cultures will produce competing alleles
   at some loci; the confidence score will pick one, and the `~` annotation is often the only
   visible hint.

## 11. Limitations

1. **Oxford Nanopore only.** There is no short-read path. Every filtering and alignment
   parameter is tuned for the ONT error profile, and the samplesheet takes a directory of
   ONT FASTQ files rather than read pairs. Illumina data needs a different pipeline.
2. **No novel allele detection or submission.** A sequence that is not in PubMLST is reported
   as `~N` against the closest known allele. NAKAST will not tell you it is new, propose a
   number, or prepare a submission. Confirming a candidate novel allele — by Sanger, for
   instance — is a manual step, and the consensus in `consensus_sequences/` is the starting
   point.
3. **Network required.** There is no offline mode and no local database cache between runs.
   Every run re-downloads the scheme.
4. **Validated on one species.** The architecture is species-agnostic and was exercised on
   *Salmonella*, *Brucella*, *Vibrio* and *Mycoplasma genitalium* schemes, but biological
   validation against known isolates was done only for *S. agalactiae* with the in-house ISP
   amplicon panel. Alignment parameters are tuned for that panel.
5. **Clonal complexes depend on the scheme.** 33 of 135 schemes define none, and even where
   defined, many STs have no CC. `CC = -` is frequently correct.
6. **No contamination or mixed-sample detection.** There is no explicit check for multiple
   alleles at a locus.
7. **Depth thresholds are global.** `--min_depth` applies to all loci equally. A panel where
   one amplicon systematically underperforms may need the threshold lowered for the whole
   run.
8. **The report is per species.** Batches spanning several species produce several files
   rather than one merged table, because the locus columns differ.

## 12. Parameter tuning notes

Two findings from tuning against real *S. agalactiae* data are worth recording, because they
are counter-intuitive and easy to reintroduce.

**KMA's `-mrc` is not allele coverage.** `-mrc` is *minimum query coverage*: the fraction of
the **read** that must align. An earlier version passed `--allele_coverage` to it. With reads
averaging ~950 bp against ~500 bp amplicons, most reads cannot reach 90% query coverage; loci
with abundant reads survived anyway, but weakly amplified loci lost every read and vanished
from the results despite being perfect matches at 100% identity and coverage. The flag was
removed. Allele coverage is enforced downstream on `Template_Coverage`, where it belongs.

**filtlong's quality thresholds are not on the Phred scale.** `--min_mean_q` and
`--min_window_q` take a 0–100 accuracy percentage, so passing `20` filters nothing at all
(Q20 corresponds to 99). Setting them to a value that does filter turned out to be harmful:
at 95 the weakly amplified loci lost all support, because low-abundance loci also tend to
carry the lowest-quality reads. The flags were removed and quality is controlled solely by
chopper, on the Phred scale, through `--nano_base_quality`.

A related negative result: escalating quality tiers (Q30 → Q25 → Q20) is not viable for
typical ONT amplicon data. With a median per-read quality near Q18, thresholds above ~22
retain a fraction of a percent of bases, and the surviving fragments are shorter than a
single amplicon, so they cannot cover an allele.

## 13. Troubleshooting

**`Unknown configuration profile: 'conda'`** — Conda is enabled by default now; drop the
`-profile conda` flag, or check that the `conda { }` scope in `nextflow.config` uses bare
keys (`enabled = true`, not `conda.enabled = true`) since it sits at the top level.

**`command not found` / exit status 127** — the process ran against the host `PATH` instead
of its Conda environment. Confirm `nextflow config .` reports `conda { enabled = true }`,
and that no stray `nextflow.config` in your launch directory is overriding it.

**`Variable declarations cannot be mixed with config statements`** — a `nextflow.config` in
your launch directory uses syntax that Nextflow 26 rejects. Nextflow merges the config from
the launch directory with the pipeline's own, so an unrelated config from an old project
will break the run. Launch from a clean directory.

**Every ST is `-`** — inspect the allele columns first. Annotated alleles (`~N`, `N?`, `INS`)
cannot match a profile. If a single locus is consistently `-`, check its depth in
`reports/<sample>.res`; it may be an amplification problem rather than an analysis one.

**Species rejected by validation** — run `--list_species` and use the exact short name. The
error message suggests near matches.

**Download fails** — the pipeline retries three times before stopping, and lets in-flight QC
finish. Re-run with `-resume` when connectivity returns; completed work is reused.

**Nothing is cached on `-resume`** — check that nothing in the task inputs changes between
runs. Interpolating a `Path` object such as `launchDir` directly into a process script gives
it an unstable hash; pass it as a `val` input instead.

## 14. Reproducibility

Every process declares its own Conda environment with exact versions:

| Process | Environment |
|---|---|
| `VALIDATE_SAMPLESHEET` | `python=3.13.11 pandas=2.3.3` |
| `DOWNLOAD_PREP_DB`, `KMA_RUN` | `python=3.13.11 kma=1.6.8` |
| `concat_ONT_fastq` | `python=3.13.11 coreutils=9.5 gzip=1.12` |
| `FILTER_ONT` | `python=3.13.11 filtlong=0.3.1 chopper=0.12.0 gzip=1.12` |
| `NANOPLOT` | `python=3.13.11 nanoplot=1.46.2` |
| `MULTIQC` | `python=3.13.11 multiqc=1.33` |
| `GENERATE_REPORT` | `python=3.13.11 pandas=2.3.3 numpy=2.4.0 openpyxl=3.1.5` |
| `LIST_SPECIES` | `python=3.13.11` |

Environments are cached in `$HOME/.nextflow/conda` and built with mamba. Identical
specifications across processes share one environment.

The one input that is *not* pinned is PubMLST itself, which changes as curators add alleles
and STs. To make a past run reproducible, keep `reports/<species>_profiles.tsv` and the
`pipeline_info/` trace together with the report.
