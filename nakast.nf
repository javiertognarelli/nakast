#!/usr/bin/env nextflow

// NAKAST - MLST typing from Oxford Nanopore amplicon sequencing.
//
// Designed and validated with Streptococcus agalactiae. The species is a
// per-sample parameter, so the pipeline works with any MLST scheme published
// by PubMLST; see docs/supported_species.md for the catalogue and
// docs/USER_MANUAL.md for design rationale, assumptions and limitations.
//
// Author:          Javier Tognarelli - Genomica UV
// Commissioned by: ISP (Daniel Escobar, Fernando Amaya)
// Panel:           in-house design, ISP 2025
// Created:         December 2025

nextflow.enable.dsl=2

// Run-level inputs and outputs
params.samplesheet = 'samplesheet.tsv'
params.outdir = 'results'

// Analysis parameters
params.nano_base_quality = 20
params.mlst_report = "mlst_profiles"
params.min_depth = 30
params.allele_coverage = 90
params.min_identity = 90
params.min_length = 300
params.keep_percent = '80'

// Read quality is enforced by chopper alone. filtlong's --min_mean_q and
// --min_window_q are deliberately left unset, for two reasons:
//   1. They use a 0-100 accuracy scale rather than Phred, so passing a Phred
//      value filters nothing at all (Q20 == 99, Q25 == 99.7, Q30 == 99.9).
//   2. Setting them to an equivalent threshold removes weakly amplified loci
//      outright: low-abundance loci also carry the lowest-quality reads, and
//      benchmarking showed such loci falling from >30x depth to zero.

params.generate_consensus = true
params.qc_outdir = "${params.outdir}/qc"
params.consensus_outdir = "${params.outdir}/consensus_sequences"
params.report_outdir = "${params.outdir}/reports"

params.run_name = 'NAKAST_Run'
params.run_description = 'NAKAST: MLST typing from Oxford Nanopore reads, for any PubMLST scheme'

// Catalogue of supported schemes, used to validate the 'species' column
params.species_catalogue = "$projectDir/assets/pubmlst_species.tsv"
params.kma_k = 31

params.qc_only = false
params.list_species = false
params.help = false

def print_help() {
    log.info """
        Usage:
        nextflow run nakast.nf [options]

        Description:
        NAKAST determines MLST profiles from Oxford Nanopore reads. The species
        is declared per sample in the 'species' column of the samplesheet, so a
        single batch may mix species.

        Main options:
        --samplesheet        Input sample table (default: samplesheet.tsv)
        --outdir             Base output directory (default: results)

        MLST options:
        --mlst_report        Base name of the MLST report (default: mlst_profiles)
        --min_depth          Minimum depth to call an allele (default: 30)
        --min_identity       Minimum identity (%) (default: 90)
        --allele_coverage    Minimum allele coverage (%) (default: 90)
        --generate_consensus Write per-locus consensus sequences (default: true)

        Read filtering options:
        --nano_base_quality  Minimum Phred base quality (default: 20)
        --min_length         Minimum read length (default: 300)
        --keep_percent       Keep this percentage of the best reads (default: 80)

        Output directories:
        --qc_outdir          Read QC results
        (default: results/qc)

        --consensus_outdir   Consensus sequences
        (default: results/consensus_sequences)

        --report_outdir      Alignment results and profile tables
        (default: results/reports)


        Run modes:
        --qc_only            Run quality control only (default: false)
        --list_species       List the supported PubMLST species and exit

        Other:
        --kma_k              K-mer size for the KMA index (default: 31)
        --help               Print this message and exit

        Samplesheet (TSV with header):
        sample_id  fastq_dir   species
        M1         data/M1     sagalactiae
        M2         data/M2     salmonella

        The 'species' column takes the names listed in
        docs/supported_species.md (135 schemes).

        Example:
        nextflow run nakast.nf --samplesheet samples.tsv --outdir results --min_depth 40

    """.stripIndent()
}
workflow PRINCIPAL {
    main:
        // 1. Resolve inputs
        ch_input = file(params.samplesheet, checkIfExists: true, followLinks: true)
        ch_catalogue = file(params.species_catalogue, checkIfExists: true)

        // 2. Pre-flight validation. Every downstream channel derives from
        // its output, so an invalid samplesheet halts the run before any
        // expensive work starts.
        VALIDATE_SAMPLESHEET(ch_input, "${launchDir}", ch_catalogue)

        // 3. Build the sample channel. Database downloads are launched
        // further down, once the species present in the run are known.
        VALIDATE_SAMPLESHEET.out.ok
            .map { file(params.samplesheet, checkIfExists: true, followLinks: true) }
            .splitCsv(header:true, sep:'\t')
            .map { row -> 
                def sample_info = [id: row.sample_id, species: row.species.trim()]
                return [ sample_info, file(row.fastq_dir, checkIfExists: true, followLinks: true)]
            }
            .set { ch_reads }
        
        ch_reads
            | concat_ONT_fastq
            | FILTER_ONT

        nanoplot_out = NANOPLOT(FILTER_ONT.out.filtered_reads)
        qc_dirs_ch = nanoplot_out.map { sample, qc_dir -> qc_dir }.collect()
        MULTIQC(qc_dirs_ch)  // aggregate every per-sample QC folder in one report

        // One database per distinct species; 'unique' avoids re-downloading
        // the same scheme for every sample that shares it.
        ch_species = ch_reads.map { sample, _reads -> sample.species }.unique()
        DOWNLOAD_PREP_DB(ch_species)

        // Join each sample to the database built for its own species.
        ch_kma = FILTER_ONT.out.filtered_reads
            .map { sample, reads -> [ sample.species, sample, reads ] }
            .combine(DOWNLOAD_PREP_DB.out.mlst_db, by: 0)
        KMA_RUN(ch_kma)

        // One report per species: loci differ between schemes and cannot
        // share a single table of columns.
        ch_reporte = KMA_RUN.out.kma_result
            .groupTuple()
            .join(DOWNLOAD_PREP_DB.out.mlst_profiles)
        GENERATE_REPORT(ch_reporte)
}
workflow list_species {
    main:
        LIST_SPECIES()
}
workflow qc_only {
    main:
        ch_input = file(params.samplesheet, checkIfExists: true, followLinks: true)
        ch_catalogue = file(params.species_catalogue, checkIfExists: true)

        // Same pre-flight validation as PRINCIPAL: the read channel derives
        // from its output, so nothing runs on an invalid samplesheet.
        VALIDATE_SAMPLESHEET(ch_input, "${launchDir}", ch_catalogue)

        VALIDATE_SAMPLESHEET.out.ok
            .map { file(params.samplesheet, checkIfExists: true, followLinks: true) }
            .splitCsv(header:true, sep:'\t')
            .map { row -> 
                def sample_info = [id: row.sample_id, species: row.species.trim()]
                return [ sample_info, file(row.fastq_dir, checkIfExists: true, followLinks: true)]
            }
            .set { ch_reads }

        ch_reads
            | concat_ONT_fastq
            | FILTER_ONT

        nanoplot_out = NANOPLOT(FILTER_ONT.out.filtered_reads)
        qc_dirs_ch = nanoplot_out.map { sample, qc_dir -> qc_dir }.collect()
        MULTIQC(qc_dirs_ch)  // aggregate every per-sample QC folder in one report
}
workflow {
    // Handled inside the workflow rather than at script level: Nextflow 26's
    // strict syntax requires statements to live in a process, workflow or
    // function.
    if (params.help) {
        print_help()
        return
    }

    if (params.list_species) {
        list_species()
    }
    else if (params.qc_only) {
        qc_only()
    }
    else {
        PRINCIPAL()
    }
}
process VALIDATE_SAMPLESHEET {
    tag "validacion"
    conda 'conda-forge::python=3.13.11 conda-forge::pandas=2.3.3'
    label 'process_low'
    // Overrides the global 'ignore' strategy: an invalid samplesheet must
    // stop the run rather than be skipped silently.
    errorStrategy 'terminate'

    input:
        path samplesheet
        // launchDir is passed as a String instead of being interpolated into
        // the script body. Interpolating the Path object puts it in the task's
        // hashed context, where its hash is unstable across runs and breaks
        // -resume caching.
        val basedir
        // Scheme catalogue, so an unknown species fails here rather than
        // after a partial download.
        path catalogue
    output:
        path "validacion.ok", emit: ok

    script:
        // Redirection rather than a pipe: Nextflow runs with `bash -ue` and
        // without pipefail, so a pipe would mask the script's exit code.
        """
        validate_samplesheet.py ${samplesheet} --basedir ${basedir} \\
            --catalogue ${catalogue} > validacion.ok \\
            || { cat validacion.ok >&2; exit 1; }
        cat validacion.ok
        """
}
process DOWNLOAD_PREP_DB {
    tag "$species"
    conda 'conda-forge::python=3.13.11 bioconda::kma=1.6.8'
    label 'process_low'
    publishDir "${params.report_outdir}", mode: 'copy', pattern: "*_profiles.tsv"

    // Overrides the global 'ignore' strategy: without a database there is no
    // typing, so a skipped failure would yield a run with no results.
    // Retries cover transient network faults; 'finish' then lets in-flight QC
    // complete before stopping, so a later -resume reuses it and repeats only
    // the download.
    errorStrategy { task.attempt <= 3 ? 'retry' : 'finish' }
    maxRetries 3

    input:
        val species
    output:
        tuple val(species), path("${species}_profiles.tsv"), path("${species}_loci.txt"), emit: mlst_profiles
        tuple val(species), path("${species}_db.*"), emit: mlst_db
    script:
        // download_pubmlst.py detects the MLST scheme (not always id 1) and
        // reads its locus list from the scheme definition (not always seven).
        """
        download_pubmlst.py --species ${species} --outdir .

        kma index -i ${species}_alelos.fasta -k ${params.kma_k} -o ${species}_db
        """
}
process concat_ONT_fastq {
    tag "$sample.id"
    conda 'conda-forge::python=3.13.11 conda-forge::coreutils=9.5 conda-forge::gzip=1.12'
    // A failed sample is marked as such and the rest of the batch continues
    errorStrategy 'ignore'
    label 'process_medium'

    input:
        tuple val(sample), path(input_dir)
    output:
        tuple val(sample), path("${sample.id}.unfiltered.fastq.gz"), emit: unfiltered_reads
    script:
        """
        if ls ${input_dir}/*.fastq.gz > /dev/null 2>&1; then
            echo "Concatenando archivos comprimidos..."
            cat ${input_dir}/*.fastq.gz > ${sample.id}.unfiltered.fastq.gz
        
        # Fall back to uncompressed .fastq
        elif ls ${input_dir}/*.fastq > /dev/null 2>&1; then
            cat ${input_dir}/*.fastq | gzip > ${sample.id}.unfiltered.fastq.gz
        
        # Neither present: fail this sample only
        else
            # Surfaced in .nextflow.log
            echo "ERROR: sample ${sample.id} is empty or malformed" >&2
            # errorStrategy 'ignore' confines the failure to this sample
            exit 1
        fi
        """
}
process FILTER_ONT {
    tag "$sample.id"
    conda 'conda-forge::python=3.13.11 bioconda::filtlong=0.3.1 bioconda::chopper=0.12.0 conda-forge::gzip=1.12'
    // Intermediate output, not published. Uncomment to keep the filtered reads:
    // publishDir "${params.outdir}/ont_filtered", mode: 'copy'
    label 'process_medium'

    input:
    tuple val(sample), path(reads)

    output:
    tuple val(sample), path("${sample.id}.fastq.gz"), emit: filtered_reads

    script:
    """
    # filtlong: length filter, then keep the best params.keep_percent of reads
    #           (its ranking weights mean and window quality).
    # chopper:  Phred quality filter; splits reads at low-quality stretches.

    filtlong --keep_percent ${params.keep_percent} \
        --min_length ${params.min_length} \
        --mean_q_weight 5 \
        --window_q_weight 10 --window_size 50 ${reads} |
    chopper -q ${params.nano_base_quality} --minlength 50 --trim-approach split-by-low-quality --cutoff ${params.nano_base_quality} |
    gzip > ${sample.id}.fastq.gz
    """
}
process NANOPLOT {
    tag "$sample.id"
    conda 'conda-forge::python=3.13.11 bioconda::nanoplot=1.46.2'
    publishDir "${params.qc_outdir}", mode: 'copy'
    label 'process_medium'

    input:
    tuple val(sample), path(reads)

    output:
    tuple val(sample), path("qc_${sample.id}")

    script:
    """
    NanoPlot \
        --fastq ${reads} \
        --outdir qc_${sample.id} \
        --prefix ${sample.id}_ \
        --threads ${task.cpus} \
        --tsv_stats
    """
}
process MULTIQC {
    tag "multiqc"
    conda 'conda-forge::python=3.13.11 bioconda::multiqc=1.33'
    publishDir "${params.qc_outdir}", mode: 'copy'
    label 'process_medium'

    input:
        // All qc_* folders at once, so MultiQC runs a single time
        path(qc_dirs)
    output:
        path "multiqc_report.html"
        path "multiqc_data"
        path "multiqc_plots"
    script:
        """
        multiqc --force --interactive -p -v ${qc_dirs} -o .
        """
}
process KMA_RUN {
    tag "$sample.id ($species)"
    conda 'conda-forge::python=3.13.11 bioconda::kma=1.6.8'
    publishDir "${params.report_outdir}", mode: 'copy', pattern: "*.res"
    label 'process_high'
    // Overrides the global 'ignore' strategy: a failure here leaves the run
    // without MLST results, and 'ignore' would exit 0 with no report and no
    // warning.
    errorStrategy 'terminate'

    // 'enabled' rather than an if() block: Nextflow 26's strict syntax does
    // not allow conditionals inside a process body.
    publishDir "${params.consensus_outdir}", mode: 'copy', pattern: "*.fsa", enabled: params.generate_consensus

    input:
        tuple val(species), val(sample), path(reads), path(mlst_db_files)
    output:
        tuple val(species), path("${sample.id}.res"), emit: kma_result
        path "${sample.id}.fsa", emit: consensus_sequences
    script:
        // allele_coverage is intentionally NOT passed to -mrc. That flag is
        // "minimum query coverage", the aligned fraction of the READ, not of
        // the allele. With reads roughly twice the amplicon length it discards
        // loci that match the reference perfectly. Allele coverage is enforced
        // downstream in parse_kma.py via Template_Coverage.
        coverage = params.allele_coverage / 100
        """
        kma -i ${reads} -t_db ${species}_db -nf -t ${task.cpus} \\
            -ID ${params.min_identity} -1t1 \\
            -mrs ${coverage} -bc ${coverage} -eq ${params.nano_base_quality} -bcNano -lc \\
            -mq 30 -md ${params.min_depth} -bcd ${params.min_depth} -mi ${params.min_depth} \\
            -ef \\
            -reward 2 -penalty 6 -gapopen 15 -gapextend 3 -Npenalty 5 -o ${sample.id}
        """
}
process GENERATE_REPORT {
    tag "$species"
    conda 'conda-forge::python=3.13.11 conda-forge::pandas=2.3.3 conda-forge::numpy=2.4.0 conda-forge::openpyxl=3.1.5'
    publishDir "${params.outdir}", mode: 'copy', pattern: "${params.mlst_report}_*"
    label 'process_medium'
    // Overrides the global 'ignore' strategy: a failure here leaves the run
    // without MLST results, and 'ignore' would exit 0 with no report and no
    // warning.
    errorStrategy 'terminate'

    input:
        tuple val(species), path(kma_results), path(mlst_profiles), path(mlst_loci)
    output:
        path "${params.mlst_report}_${species}.txt"
        path "${params.mlst_report}_${species}.xlsx"
    script:
        """
        parse_kma.py -i . -p ${mlst_profiles} --loci ${mlst_loci} \\
            -o ${params.mlst_report}_${species} \\
            --min_depth ${params.min_depth} \\
            --min_identity ${params.min_identity} \\
            --min_coverage ${params.allele_coverage}
        """
}
process LIST_SPECIES {
    tag "pubmlst_catalogue"
    conda 'conda-forge::python=3.13.11'
    label 'process_low'
    errorStrategy 'terminate'

    output:
        path "supported_species.txt"

    script:
        """
        list_pubmlst_species.py --tabla > supported_species.txt \\
            || { cat supported_species.txt >&2; exit 1; }
        cat supported_species.txt
        """
}
