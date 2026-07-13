#!/usr/bin/env python3
import sys
import pandas as pd
import os

def validate_samplesheet(file_path):
    errors = []
    
    try:
        df = pd.read_csv(file_path, sep='\t')
    except Exception as e:
        sys.exit(f"CRITICAL: No se pudo leer el archivo CSV. {e}")

    # 1. Validar Columnas Requeridas
    # Nota: Permitimos que las columnas existan aunque estén vacías en algunas filas
    required_cols = ['sample_id', 'platform', 'fastq_1', 'fastq_2', 'fastq_dir']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        sys.exit(f"ERROR: Faltan columnas en el header: {missing_cols}")

    # Normalizar platform a minúsculas y quitar espacios
    if 'platform' in df.columns:
        df['platform'] = df['platform'].astype(str).str.lower().str.strip()
        df['sample_id'] = df['sample_id'].astype(str).str.strip()

    # 2. Validar integridad de sample_id y platform (No vacíos)
    if df['sample_id'].eq('nan').any() or df['sample_id'].eq('').any():
         errors.append("Fila(s) con 'sample_id' vacío detectada(s).")
    
    if df['platform'].eq('nan').any() or df['platform'].eq('').any():
         errors.append("Fila(s) con 'platform' vacío detectada(s).")

    # Validar duplicados en sample_id
    if df['sample_id'].duplicated().any():
        dups = df.loc[df['sample_id'].duplicated(), 'sample_id'].unique()
        errors.append(f"sample_id duplicados encontrados: {dups}")

    # 3. Validación Condicional Lógica (Iteramos para detalle específico)
    for index, row in df.iterrows():
        line_num = index + 2  # +2 porque index inicia en 0 y hay header
        pid = row['sample_id']
        platform = row['platform']

        # Validación NANOPORE
        if platform == 'nanopore':
            f_dir = row['fastq_dir']
            
            # Check si está vacío (pandas lee vacíos como NaN/float)
            if pd.isna(f_dir) or str(f_dir).strip() == '':
                errors.append(f"[Fila {line_num} - {pid}] Nanopore requiere 'fastq_dir'.")
            # Check si existe la ruta
            elif not os.path.exists(str(f_dir)):
                errors.append(f"[Fila {line_num} - {pid}] Ruta fastq_dir no existe: {f_dir}")

        # Validación ILLUMINA
        elif platform == 'illumina':
            f1 = row['fastq_1']
            f2 = row['fastq_2']

            # Check fastq_1
            if pd.isna(f1) or str(f1).strip() == '':
                errors.append(f"[Fila {line_num} - {pid}] Illumina requiere 'fastq_1'.")
            elif not os.path.exists(str(f1)):
                errors.append(f"[Fila {line_num} - {pid}] Archivo fastq_1 no existe: {f1}")
            
            # Check fastq_2
            if pd.isna(f2) or str(f2).strip() == '':
                errors.append(f"[Fila {line_num} - {pid}] Illumina requiere 'fastq_2'.")
            elif not os.path.exists(str(f2)):
                errors.append(f"[Fila {line_num} - {pid}] Archivo fastq_2 no existe: {f2}")

        # Plataforma desconocida
        elif platform not in ['nanopore', 'illumina']:
            errors.append(f"[Fila {line_num} - {pid}] Plataforma desconocida: '{platform}'. Use 'illumina' o 'nanopore'.")

    # 4. Reporte Final
    if errors:
        print("----------------------------------------------------------------")
        print("❌ ERRORES EN SAMPLESHEET DETECTADOS:")
        for e in errors:
            print(f" - {e}")
        print("----------------------------------------------------------------")
        sys.exit(1) # Salida con error para detener Nextflow
    else:
        print(f"✅ Samplesheet validado correctamente: {len(df)} muestras encontradas.")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python check_samplesheet.py <samplesheet.csv>")
    validate_samplesheet(sys.argv[1])
