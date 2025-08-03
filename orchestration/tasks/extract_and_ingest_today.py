from prefect import task
from datetime import datetime
from pathlib import Path
import pandas as pd
import requests
import boto3
import re

# --- Configuración general ---
S3_BUCKET = "mlops-milk-datalake"
BASE_URL = "https://www.economia-sniim.gob.mx/SNIIM-Archivosfuente/Comentarios/Otros"

# Diccionario de meses en español
meses_es_a_en = {
    "enero": "January",
    "febrero": "February",
    "marzo": "March",
    "abril": "April",
    "mayo": "May",
    "junio": "June",
    "julio": "July",
    "agosto": "August",
    "septiembre": "September",
    "octubre": "October",
    "noviembre": "November",
    "diciembre": "December",
}


@task(name="extract_and_ingest_today", retries=2, retry_delay_seconds=30)
def extract_and_ingest_today(execution_date: datetime = None) -> str:
    execution_date = (
        execution_date.date() if execution_date else datetime.today().date()
    )

    # Rutas dinámicas
    excel_filename = f"Leche{execution_date.strftime('%d%m%Y')}.xlsx"
    excel_url = f"{BASE_URL}/{excel_filename}"
    excel_path = f"data/raw/{excel_filename}"

    parquet_filename = f"{execution_date.strftime('%Y-%m-%d')}-data.parquet"
    local_parquet_path = f"data/datalake/daily/{execution_date.year}/{execution_date.strftime('%m')}/{parquet_filename}"
    s3_key = f"daily/{execution_date.year}/{execution_date.strftime('%m')}/{parquet_filename}"

    # --- Descargar Excel ---
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    response = requests.get(excel_url)
    if response.status_code != 200:
        raise Exception(f"❌ Failed to download Excel file: {response.status_code}")
    with open(excel_path, "wb") as f:
        f.write(response.content)

    # --- Parseo ---
    df_all = parse_excel_to_df(excel_path)
    df_today = df_all[df_all["Fecha"] == execution_date].copy()
    if df_today.empty:
        raise ValueError("❌ No rows found for the given execution date.")

    # --- Guardar localmente ---
    Path(local_parquet_path).parent.mkdir(parents=True, exist_ok=True)
    df_today.to_parquet(local_parquet_path, index=False)

    # --- Subir a S3 ---
    s3 = boto3.client("s3")
    with open(local_parquet_path, "rb") as f:
        s3.upload_fileobj(f, S3_BUCKET, s3_key)

    return f"s3://{S3_BUCKET}/{s3_key}"


def parse_excel_to_df(path):
    df = pd.read_excel(path, header=None)
    data_final = []

    for i, row in df.iterrows():
        if (
            row.astype(str)
            .str.contains(
                "Precio promedio al consumidor por litro", case=False, na=False
            )
            .any()
        ):
            row_fecha = df.iloc[i + 1]
            fecha_raw = next(
                (
                    str(cell)
                    for cell in row_fecha
                    if isinstance(cell, str) and "de" in cell
                ),
                None,
            )
            if not fecha_raw:
                continue

            match = re.search(
                r"(\d{1,2}) de (\w+) de (\d{4})", fecha_raw, re.IGNORECASE
            )
            if not match:
                continue
            dia, mes, año = match.groups()
            mes_en = meses_es_a_en.get(mes.lower())
            if not mes_en:
                continue
            fecha = pd.to_datetime(f"{dia} {mes_en} {año}", dayfirst=True).date()

            enc2 = df.iloc[i + 3, 2:6].values
            columnas = ["Estado", "Ciudad"]
            for j in range(4):
                tipo = "Pasteurizada" if j < 2 else "Ultrapasteurizada"
                canal = enc2[j]
                columnas.append(f"{tipo}_{canal}")

            df_bloque = df.iloc[i + 4 :, 0:6].copy()
            df_bloque.columns = columnas
            df_bloque[["Estado", "Ciudad"]] = df_bloque[["Estado", "Ciudad"]].ffill()

            stop_idx = None
            for k, row_k in df_bloque.iterrows():
                celda = str(row_k[0]).strip().lower()
                if (
                    "promedio" in celda
                    or "fuente" in celda
                    or "sniim" in celda
                    or celda == "estado"
                    or celda == "nan"
                ):
                    stop_idx = k
                    break
            if stop_idx:
                df_bloque = df_bloque.loc[: stop_idx - 1]

            df_bloque["Fecha"] = fecha
            df_long = df_bloque.melt(
                id_vars=["Fecha", "Estado", "Ciudad"],
                var_name="Tipo_Canal",
                value_name="Precio",
            )

            df_long["Tipo"] = df_long["Tipo_Canal"].str.split("_").str[0]
            df_long["Canal"] = df_long["Tipo_Canal"].str.split("_").str[1]
            df_long = df_long[["Fecha", "Estado", "Ciudad", "Tipo", "Canal", "Precio"]]
            df_long["Precio"] = pd.to_numeric(df_long["Precio"], errors="coerce")

            data_final.append(df_long)

    df_final = pd.concat(data_final, ignore_index=True)
    df_final = df_final[
        ~df_final["Ciudad"].str.lower().str.contains("promedio", na=False)
    ]
    return df_final
