# simulate_publication_daily.py

import os
import re
import boto3
import pandas as pd
from pathlib import Path
from datetime import datetime
from io import BytesIO

# Config
EXCEL_URL = "https://www.economia-sniim.gob.mx/SNIIM-Archivosfuente/Comentarios/Otros/Leche30072025.xlsx"
EXCEL_FILE = "raw/milk_prices.xlsx"
UPLOAD_TO_S3 = True
S3_BUCKET = "mlops-milk-datalake"

# Month translation ES → EN
meses_es_a_en = {
    'enero': 'January', 'febrero': 'February', 'marzo': 'March',
    'abril': 'April', 'mayo': 'May', 'junio': 'June',
    'julio': 'July', 'agosto': 'August', 'septiembre': 'September',
    'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
}

def download_excel(url=EXCEL_URL, output_path=EXCEL_FILE):
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"⬇️  Downloading file from {url}")
    os.system(f"wget {url} -O {output_path}")

def parse_excel_to_df(path=EXCEL_FILE):
    df = pd.read_excel(path, header=None)
    data_final = []

    for i, row in df.iterrows():
        if row.astype(str).str.contains("Precio promedio al consumidor por litro", case=False, na=False).any():
            row_fecha = df.iloc[i + 1]
            fecha_raw = next((str(cell) for cell in row_fecha if isinstance(cell, str) and "de" in cell), None)
            if not fecha_raw:
                continue

            match = re.search(r"(\d{1,2}) de (\w+) de (\d{4})", fecha_raw, re.IGNORECASE)
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

            df_bloque = df.iloc[i + 4:, 0:6].copy()
            df_bloque.columns = columnas
            df_bloque[['Estado', 'Ciudad']] = df_bloque[['Estado', 'Ciudad']].ffill()

            stop_idx = None
            for k, row_k in df_bloque.iterrows():
                celda = str(row_k[0]).strip().lower()
                if "promedio" in celda or "fuente" in celda or "sniim" in celda or celda == "estado" or celda == "nan":
                    stop_idx = k
                    break

            if stop_idx:
                df_bloque = df_bloque.loc[:stop_idx - 1]

            df_bloque["Fecha"] = fecha
            df_long = df_bloque.melt(id_vars=["Fecha", "Estado", "Ciudad"],
                                     var_name="Tipo_Canal", value_name="Precio")

            df_long["Tipo"] = df_long["Tipo_Canal"].str.split("_").str[0]
            df_long["Canal"] = df_long["Tipo_Canal"].str.split("_").str[1]
            df_long = df_long[["Fecha", "Estado", "Ciudad", "Tipo", "Canal", "Precio"]]
            df_long["Precio"] = pd.to_numeric(df_long["Precio"], errors="coerce")

            data_final.append(df_long)

    df_final = pd.concat(data_final, ignore_index=True)
    df_final = df_final[~df_final["Ciudad"].str.lower().str.contains("promedio", na=False)]
    return df_final

def save_daily_partitions(df: pd.DataFrame, output_root="../data/datalake/daily"):
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Año"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.month
    df["Día"] = df["Fecha"].dt.day

    for (año, mes, dia), df_group in df.groupby(["Año", "Mes", "Día"]):
        filename = f"{año}-{mes:02d}-{dia:02d}-data.parquet"
        local_path = f"{output_root}/{año}/{mes:02d}/{filename}"

        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        df_group.drop(columns=["Año", "Mes", "Día"]).to_parquet(local_path, index=False)
        print(f"✅ Saved: {local_path}")

        if UPLOAD_TO_S3:
            s3_key = f"daily/{año}/{mes:02d}/{filename}"
            upload_to_s3(local_path, S3_BUCKET, s3_key)

def upload_to_s3(local_path, bucket, s3_key):
    s3 = boto3.client("s3")
    with open(local_path, "rb") as f:
        s3.upload_fileobj(f, bucket, s3_key)
    print(f"☁️ Uploaded to S3: s3://{bucket}/{s3_key}")

def main():
    download_excel()
    df = parse_excel_to_df()
    save_daily_partitions(df)

if __name__ == "__main__":
    main()
