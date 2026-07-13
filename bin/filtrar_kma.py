#!/usr/bin/env python3
import os
import glob
import pandas as pd
import numpy as np
import argparse

# Configuración
MIN_DEPTH = 30.0       # Profundidad mínima absoluta para creerle al alelo
MIN_IDENTITY = 90.0    # Identidad mínima
MIN_COVERAGE = 90.0    # Cobertura mínima
GENES_ESPERADOS = 7    # Número de genes del esquema

def procesar_muestra(filepath, depth_threshold=MIN_DEPTH, min_identity=MIN_IDENTITY, min_coverage=MIN_COVERAGE):
    nombre_muestra = os.path.basename(filepath).replace(".res", "")

    # Cargar archivo .res (saltando las líneas de comentario si las hay)
    try:
        # KMA output suele tener header. Ajustar si no tiene header.
        df = pd.read_csv(filepath, sep="\t")
    except Exception as e:
        print(f"[ERROR] No se pudo leer {filepath}: {e}")
        return

    # Limpiar nombres de columnas (quitar espacios extra)
    df.columns = df.columns.str.strip()

    # Filtrar basura absoluta por profundidad e identidad
    df_clean = df[ (df['Depth'] >= depth_threshold) ].copy()

    # Extraer nombre del gen del Template (formato 'gen_numero' o 'gen-numero')
    # Ajustar esta lógica si cambia en el futuro cómo se llamen los alelos en la DB
    # Ejemplo: 'glcK_172' -> Gen: 'glcK', Alelo: 'glcK_172'
    df_clean['Gen_Name'] = df_clean['#Template'].apply(lambda x: x.split('_')[0] if '_' in x else x.split('-')[0])
    df_clean['Alelo'] = df_clean['#Template'].apply(lambda x: x.split('_')[1] if '_' in x else x.split('-')[1])

    # Seleccionar el ganador por gen (el que tenga mayor Score)
    # Ordenamos por Score descendente y quitamos duplicados de Gen_Name
    ganadores = status_alelo(df_clean, min_identity, min_coverage)

    # Verificar resultados
    genes_encontrados = len(ganadores)

    status = "OK"
    if genes_encontrados < GENES_ESPERADOS:
        status = f"INCOMPLETO ({genes_encontrados}/{GENES_ESPERADOS})"

    orden = ['adhP', 'pheS', 'atr', 'glnA', 'sdhA', 'glcK', 'tkt']
    # Aquí imprime formato de los alelos. Primero ordenamos por los genes tal como salen en la tabla de alelos de PubMLST
    ganadores['Gen_Name'] = pd.Categorical(ganadores["Gen_Name"], categories=orden, ordered=True)

    # terminamos de ordenar y eliminarmos inidices antes de transponer tabla
    ganadores = ganadores.sort_values("Gen_Name").set_index("Gen_Name")
    perfil = ganadores[['Alelo']].T
    perfil.insert(0, 'Muestra', nombre_muestra)
    perfil["Perfil"] = status

    return perfil

def status_alelo(df, min_identity=MIN_IDENTITY, min_coverage=MIN_COVERAGE, min_depth=30, perfect_bonus=1.5):

    df = df.copy()
    df["Alelo"] = df["Alelo"].astype(str)

    # Filtro previo por profundidad mínima — antes de cualquier lógica
    df = df[df["Depth"] >= min_depth].copy()

    # Métricas normalizadas
    df["Score_Ratio"]    = df["Score"] / df["Expected"]
    df["Score_per_depth"] = df["Score"] / (df["Depth"] * df["Template_length"])

    # _is_perfect como bonus multiplicativo, no como override absoluto
    # Un match perfecto necesita también tener buen soporte estadístico para ganar
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

    # Ahora Confidence sola ordena — el match perfecto tiene ventaja pero no garantía
    df = (
        df.sort_values(
            by=["Gen_Name", "Confidence"],
            ascending=[True, False]
        )
        .drop_duplicates(subset="Gen_Name", keep="first")
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

    df["Alelo"] = np.select(
        [
            qcov_ins,
            qcov_exact & exact_ident & exact_tcov,
            qcov_exact & ~exact_ident & exact_tcov,
            qcov_trunc & good_ident & good_tcov,
            ~good_ident | ~good_tcov,
        ],
        [
            "INS",
            df["Alelo"],
            "~" + df["Alelo"],
            df["Alelo"] + "?",
            "-",
        ],
        default="-"
    )

    return df

def asignar_st(df, db_file):
    genes = ["adhP","pheS","atr","glnA","sdhA","glcK","tkt"]

    if db_file is None:
        print("[INFO] No se proporcionó archivo de perfiles MLST. Se omite asignación de ST.")
        df.insert(1, 'ST', '-')
        df.insert(2, 'CC', '-')
        return df

    try:
        db_df = pd.read_csv(db_file, sep="\t")
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo de perfiles MLST: {e}")
        df.insert(1, 'ST', '-')
        df.insert(2, 'CC', '-')
        return df

    db_df["signature"] = db_df[genes].astype(str).agg("/".join, axis=1)

    # df: columnas ['Muestra', ...genes..., 'Status']
    missing_genes = [g for g in genes if g not in df.columns]
    if missing_genes:
        df = df.copy()
    df[missing_genes] = "-"
    df["signature"] = df[genes].astype(str).agg("/".join, axis=1)
    
    # detectar columna CC aunque cambie mayúsculas/nombre
    cc_aliases = {"clonal_complex", "clonal complex", "cc", "clonalcomplex"}
    cc_col = next((c for c in db_df.columns if c.strip().lower() in cc_aliases), None)
    cols = ["ST", "signature"] + ([cc_col] if cc_col else [])

    out = df.merge(db_df[cols], on="signature", how="left")

    out["ST"] = out["ST"].apply(lambda x: str(int(x)) if pd.notna(x) and x != "-" else "-") #para remover decimales de ST y rellenar con guiones si no hay asignación

    if cc_col:
        out = out.rename(columns={cc_col: "CC"})
        out["CC"] = out["CC"].fillna("-")
    else:
        out["CC"] = "-"

    orden = ["Muestra", "ST", "CC",
    "adhP","pheS","atr","glnA","sdhA","glcK","tkt",
    "Perfil"]

    orden = [c for c in orden if c in out.columns]
    return out[orden].replace("", pd.NA).fillna("-")

def main():
    parser = argparse.ArgumentParser(description="Procesar archivos KMA para MLST")
    parser.add_argument("-i","--input_folder", help="Carpeta con archivos .res", required=True)
    parser.add_argument("-p","--profiles", required=False, help="Archivo de perfiles MLST")
    parser.add_argument("-o","--output", default="mlst_perfiles", help="Archivo de salida para perfiles MLST en .txt y xlsx")
    parser.add_argument("-d","--min_depth", type=int, default=MIN_DEPTH, help="Profundidad mínima para considerar un alelo")
    parser.add_argument("--min_identity", type=float, default=MIN_IDENTITY, help="Identidad mínima para considerar un alelo")
    parser.add_argument("-c","--min_coverage", type=float, default=MIN_COVERAGE, help="Cobertura mínima para considerar un alelo")
    args = parser.parse_args()

    # Ejecutar para todos los .res en la carpeta
    archivos = sorted(glob.glob(os.path.join(args.input_folder, "*.res")))

    perfiles = []

    for f in archivos:
        perfil = procesar_muestra(f, depth_threshold=args.min_depth, min_identity=args.min_identity, min_coverage=args.min_coverage)
        if perfil is not None and not perfil.empty:
            perfiles.append(perfil)

    if not perfiles and args.input_folder:
        with open(f"{args.output}.txt", "w") as f:
            f.write("No se generaron perfiles MLST")
        print(f"[INFO] No se generaron perfiles MLST. Archivo de salida creado con mensaje informativo.")
        return

    perfiles_df = pd.concat(perfiles, ignore_index=True)
    st_cc_asign_df = asignar_st(perfiles_df, args.profiles)

    st_cc_asign_df.sort_values(by='Muestra').to_csv(f"{args.output}.txt", sep="\t", index=False)
    st_cc_asign_df.sort_values(by='Muestra').to_excel(f"{args.output}.xlsx", index=False)
    print(f"[INFO] Perfiles MLST guardados en {args.output}")

if __name__ == "__main__":
    main()
