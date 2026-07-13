#!/usr/bin/env nextflow

//Pipeline para análisis de datos de secuenciación ONT de MLST por encargo ISP: Daniel Escobar - Fernando Amaya
//Panel diseño propio ISP 2025
//MLST de Streptococcus agalactiae
//Autor: Javier Tognarelli - Genómica UV
//Fecha: Diciembre 2025

nextflow.enable.dsl=2

//variables de corrida
params.samplesheet = 'samplesheet.txt'
params.outdir = 'resultados'

//variables globales 
params.nano_base_quality = 20
params.mlst_report = "mlst_perfiles"
params.min_depth = 30
params.allele_coverage = 90
params.min_identity = 90
params.min_length = 300
params.keep_percent = '80'

params.generate_consensus = true
params.qc_outdir = "${params.outdir}/qc"
params.consensus_outdir = "${params.outdir}/consensus_sequences"
params.report_outdir = "${params.outdir}/reportes"

params.run_name = 'Pipeline_Run_MLST'
params.run_description = 'Pipeline analisis MLST para Streptococcus agalactiae usando datos de ONT'

params.qc_only = false
params.help = false

def print_help() {
    log.info """
        Uso:
        nextflow run mlst_pipeline.nf [opciones]

        Descripción:
        Pipeline de análisis MLST para Streptococcus agalactiae usando lecturas ONT.

        Parámetros principales:
        --samplesheet        Archivo de entrada con las muestras (default: samplesheet.txt)
        --outdir             Directorio base de salida (default: resultados)

        Parámetros MLST:
        --mlst_report        Nombre base del reporte MLST (default: mlst_perfiles)
        --min_depth          Profundidad mínima para asignación de alelo (default: 30)
        --min_identity       Identidad mínima (%) (default: 90)
        --allele_coverage    Cobertura mínima del alelo (%) (default: 90)
        --generate_consensus Generar secuencias consenso (default: true)

        Parámetros de filtrado ONT:
        --nano_base_quality  Calidad mínima de base (default: 15)
        --min_length         Longitud mínima de lectura (default: 300)
        --keep_percent       Dejar este porcentaje de mejores lecturas para analizar (default: 80%)

        Directorios internos de salida:
        --qc_outdir          Directorio para resultados de QC
        (default: resultados/qc)

        --consensus_outdir   Directorio para secuencias consenso
        (default: resultados/consensus_sequences)

        --report_outdir      Directorio para reportes finales
        (default: resultados/reportes)


        Modos de ejecución solo control de calidad:
        --qc_only            Ejecuta solo control de calidad (default: false)

        Otros:
        --help               Mostrar este mensaje y salir

        Ejemplo:
        nextflow run mlst_pipeline.nf --samplesheet muestras.txt --outdir resultados --min_depth 40

    """.stripIndent()
}
if (params.help) {
    print_help()
    System.exit(0)
}

workflow PRINCIPAL {
    main:
        // 1. Definir el archivo de entrada
        ch_input = file(params.samplesheet, checkIfExists: true, followLinks: true)

        // 2. Ejecutar validación "Pre-flight"
        // Usamos un bloque simple de Groovy para llamar al script de Python
        // Esto corre en la máquina local antes de lanzar contenedores o jobs pesados
        def validation_cmd = "bin/validar_samplesheet.py ${ch_input}"
        
        // Ejecutamos el comando y capturamos el resultado
        def proc = validation_cmd.execute()
        proc.waitFor() // Esperamos a que termine

        // Si el script de python sale con error (exit code != 0), matamos el pipeline
        if ( proc.exitValue() != 0 ) {
            println proc.err.text // Imprimimos el error de python
            println proc.in.text  // Imprimimos el stdout de python
            error "⛔ Deteniendo pipeline por errores en el samplesheet."
        } else {
            println proc.in.text // Imprimimos el "✅ Validado"
        }

        // 3. Si pasa la validación, procedemos a descargar DB y crear los canales
        DOWNLOAD_PREP_DB()
        Channel
            .fromPath(params.samplesheet, checkIfExists: true)
            .splitCsv(header:true, sep:'\t')
            .map { row -> 
                def sample_info = [id: row.sample_id, platform: row.platform.toLowerCase()]
                if (row.platform == 'nanopore') {
                    return [ sample_info, file(row.fastq_dir, checkIfExists: true, followLinks: true)]
                } else {
                    return [ sample_info, file(row.fastq_1, checkIfExists: true, followLinks: true), file(row.fastq_2, checkIfExists: true, followLinks: true)]
                }
            }
            .branch {  //branching según tipo de plataforma, permite manejar ambos tipos de datos en un solo flujo
                nanopore: it[0].platform == 'nanopore'
            }
            .set { ch_reads }
        
        ch_reads.nanopore
            | concat_ONT_fastq
            | FILTER_ONT

        nanoplot_out = NANOPLOT(FILTER_ONT.out.filtered_reads)
        qc_dirs_ch = nanoplot_out.map { sample, qc_dir -> qc_dir }.collect() //recolectar todas las carpetas de QC
        MULTIQC(qc_dirs_ch) //ejecutar MultiQC una sola vez con todas las carpetas y fin de este paso

        KMA_RUN(FILTER_ONT.out.filtered_reads, DOWNLOAD_PREP_DB.out.mlst_db_files)
        GENERATE_REPORT(KMA_RUN.out.kma_result.collect(), DOWNLOAD_PREP_DB.out.mlst_profiles)
}
workflow qc_only {
    main:
        Channel
            .fromPath(params.samplesheet)
            .splitCsv(header:true, sep:'\t')
            .map { row -> 
                def sample_info = [id: row.sample_id, platform: row.platform.toLowerCase()]
                if (sample_info.platform == 'nanopore') {
                    return [ sample_info, file(row.fastq_dir, checkIfExists: true, followLinks: true)]
                } else {
                    return [ sample_info, file(row.fastq_1, checkIfExists: true, followLinks: true), file(row.fastq_2, checkIfExists: true, followLinks: true)]
                }
            }
            .branch {  //branching según tipo de plataforma, permite manejar ambos tipos de datos en un solo flujo
                nanopore: it[0].platform == 'nanopore'
                illumina: it[0].platform == 'illumina'
            }
            .set { ch_reads }

        ch_reads.nanopore
            | concat_ONT_fastq
            | FILTER_ONT

        nanoplot_out = NANOPLOT(FILTER_ONT.out.filtered_reads)
        qc_dirs_ch = nanoplot_out.map { sample, qc_dir -> qc_dir }.collect() //recolectar todas las carpetas de QC
        MULTIQC(qc_dirs_ch) //ejecutar MultiQC una sola vez con todas las carpetas y fin de este paso
}
workflow {
    if (params.qc_only) {
        qc_only()
    }
    else {
        PRINCIPAL() //por defecto se ejecuta el workflow principal
    }
}
process DOWNLOAD_PREP_DB {
    tag "downloading_alleles_and_profiles"
    label 'process_low'  // Usará 1 CPU y poca RAM
    publishDir "${params.report_outdir}", mode: 'copy', pattern: "*.tsv"
    output:
        path "sagalactiae.tsv", emit: mlst_profiles
        path "S_agalactiae_db.*", emit: mlst_db_files
    script:
        """
        curl --silent --output 'sagalactiae.tsv' 'https://rest.pubmlst.org/db/pubmlst_sagalactiae_seqdef/schemes/1/profiles_csv'
        curl --silent --output 'adhP.tfa' 'https://rest.pubmlst.org/db/pubmlst_sagalactiae_seqdef/loci/adhP/alleles_fasta'
        curl --silent --output 'glnA.tfa' 'https://rest.pubmlst.org/db/pubmlst_sagalactiae_seqdef/loci/glnA/alleles_fasta'
        curl --silent --output 'pheS.tfa' 'https://rest.pubmlst.org/db/pubmlst_sagalactiae_seqdef/loci/pheS/alleles_fasta'
        curl --silent --output 'sdhA.tfa' 'https://rest.pubmlst.org/db/pubmlst_sagalactiae_seqdef/loci/sdhA/alleles_fasta'
        curl --silent --output 'atr.tfa' 'https://rest.pubmlst.org/db/pubmlst_sagalactiae_seqdef/loci/atr/alleles_fasta'
        curl --silent --output 'tkt.tfa' 'https://rest.pubmlst.org/db/pubmlst_sagalactiae_seqdef/loci/tkt/alleles_fasta'
        curl --silent --output 'glcK.tfa' 'https://rest.pubmlst.org/db/pubmlst_sagalactiae_seqdef/loci/glcK/alleles_fasta'

        cat *.tfa > sagalactiae.fasta
        kma index -i sagalactiae.fasta -k 31 -o S_agalactiae_db
        """
}
process concat_ONT_fastq {
    tag "$sample.id"
    errorStrategy 'ignore' // marcará esa muestra específica como "Failed", pero continuará procesando el resto de las muestras
    label 'process_medium' // Usará ~2 CPUs y ~4GB RAM

    input:
        tuple val(sample), path(input_dir)
    output:
        tuple val(sample), path("${sample.id}.unfiltered.fastq.gz"), emit: unfiltered_reads
    script:
        """
        if ls ${input_dir}/*.fastq.gz > /dev/null 2>&1; then
            echo "Concatenando archivos comprimidos..."
            cat ${input_dir}/*.fastq.gz > ${sample.id}.unfiltered.fastq.gz
        
        # Si no, verificamos si existen archivos sin comprimir (.fastq)
        elif ls ${input_dir}/*.fastq > /dev/null 2>&1; then
            cat ${input_dir}/*.fastq | gzip > ${sample.id}.unfiltered.fastq.gz
        
        # Si no hay ninguno, lanzamos error y cortamos el proceso
        else
            # Imprimimos el error para que quede en el log (.nextflow.log)
            echo "ERROR: Muestra ${sample.id} vacía o incorrecta" >&2
            # El exit 1 le dice a Nextflow que falló.
            # Gracias a 'ignore', solo esta muestra muere aquí.
            exit 1
        fi
        """
}
process FILTER_ONT {
    tag "$sample.id"
    // No usamos publishDir aquí porque suele ser un archivo intermedio, 
    // pero para guardarlo, descomentar la línea de abajo:
    // publishDir "${params.outdir}/ont_filtered", mode: 'copy'
    label 'process_medium' // Usará ~2 CPUs y ~4GB RAM

    input:
    tuple val(sample), path(reads)

    output:
    tuple val(sample), path("${sample.id}.fastq.gz"), emit: filtered_reads

    script:
    """
    # Explicación del comando:
    # 1. gunzip -c: Descomprime el flujo de datos sin borrar el archivo original
    # 2. filtlong:  Filtra para quedarnos con las mejores lecturas (top 80% calidad o por params.keep_percent)
    # 3. chopper:   Filtra (q: calidad mínima media, l: longitud mínima 300pb)
    # 4. gzip:      Vuelve a comprimir el resultado

    filtlong --keep_percent ${params.keep_percent} \
        --min_length ${params.min_length} \
        --min_mean_q ${params.nano_base_quality} --mean_q_weight 5 \
        --window_q_weight 10 --window_size 50 \
        --min_window_q ${params.nano_base_quality} ${reads} |
    chopper -q ${params.nano_base_quality} --minlength 50 --trim-approach split-by-low-quality --cutoff ${params.nano_base_quality} |
    gzip > ${sample.id}.fastq.gz
    """
}
process NANOPLOT {
    tag "$sample.id"
    publishDir "${params.qc_outdir}", mode: 'copy' // Este SÍ queremos guardarlo para verlo
    label 'process_medium' // Usará ~2 CPUs y ~4GB RAM

    input:
    tuple val(sample), path(reads)

    output:
    tuple val(sample), path("qc_${sample.id}") // Capturamos la carpeta de salida

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
    publishDir "${params.qc_outdir}", mode: 'copy'
    label 'process_medium' // Usará ~2 CPUs y ~4GB RAM

    input:
        // Lista de carpetas qc_* (una sola vez)
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
    tag "$sample.id"
    publishDir "${params.report_outdir}", mode: 'copy', pattern: "*.res"
    label 'process_high' // Usará hasta 8 CPUs y ~8GB RAM

    if (params.generate_consensus) {
        publishDir "${params.consensus_outdir}", mode: 'copy', pattern: "*.fsa"
    }

    input:
        tuple val(sample), path(reads)
        path(mlst_db_files)
    output:
        path "${sample.id}.res", emit: kma_result
        path "${sample.id}.fsa", emit: consensus_sequences
    script:
        coverage = params.allele_coverage / 100
        """
        kma -i ${reads} -t_db S_agalactiae_db -nf -t ${task.cpus} \
            -ID ${params.min_identity} -1t1 \
            -mrs ${coverage} -bc ${coverage} -eq ${params.nano_base_quality} -bcNano -lc \
            -mq 30 -md ${params.min_depth} -bcd ${params.min_depth} -mi ${params.min_depth} \
            -mrc ${coverage} -ef \
            -reward 2 -penalty 6 -gapopen 15 -gapextend 3 -Npenalty 5 -o ${sample.id}
        """
}
process GENERATE_REPORT {
    publishDir "${params.outdir}", mode: 'copy', pattern: "${params.mlst_report}.*"
    label 'process_medium' // Usará ~2 CPUs y ~4GB RAM

    input:
        path (kma_results) // lista de archivos .res que se copia al directorio de trabajo
        path (mlst_profiles) // archivo perfiles .tsv
    output:
        path "${params.mlst_report}.txt"
        path "${params.mlst_report}.xlsx"
    script:
        """
        filtrar_kma.py -i . -p ${mlst_profiles} -o ${params.mlst_report} \
            --min_depth ${params.min_depth} \
            --min_identity ${params.min_identity} \
            --min_coverage ${params.allele_coverage}
        """
}