import pandas as pd
from datetime import datetime, timedelta
import mlflow.pyfunc
import json
from prefect import task
import boto3
from pathlib import Path


@task(name="generate_daily_predictions")
def generate_daily_predictions() -> str:
    # --- Leer el dataset completo con histórico ---
    df = pd.read_parquet("data/processed/full_dataset.parquet")

    # --- Definir la fecha objetivo ---
    tomorrow = datetime.today() + timedelta(days=1)
    fecha_pred = tomorrow.date()

    # --- Asegurarse que la columna Fecha esté en datetime ---
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # --- Obtener combinaciones únicas de dimensiones ---
    dim_cols = ["Estado", "Ciudad", "Tipo", "Canal"]
    combinations = df[dim_cols].drop_duplicates()

    # --- Calcular Precio_lag1 y Precio_mean7 ---
    records = []
    for _, row in combinations.iterrows():
        mask = (
            (df["Estado"] == row["Estado"])
            & (df["Ciudad"] == row["Ciudad"])
            & (df["Tipo"] == row["Tipo"])
            & (df["Canal"] == row["Canal"])
        )
        df_sub = df[mask].sort_values("Fecha")
        df_sub = df_sub[df_sub["Fecha"] < pd.Timestamp(fecha_pred)]

        if len(df_sub) == 0:
            continue

        precio_lag1 = df_sub.iloc[-1]["Precio"]
        precio_mean7 = df_sub.tail(7)["Precio"].mean()

        record = {
            "Estado": row["Estado"],
            "Ciudad": row["Ciudad"],
            "Tipo": row["Tipo"],
            "Canal": row["Canal"],
            "día": tomorrow.day,
            "mes": tomorrow.month,
            "año": tomorrow.year,
            "dia_semana": str(tomorrow.weekday()),
            "Precio_lag1": precio_lag1,
            "Precio_mean7": precio_mean7,
        }
        records.append(record)

    df_pred = pd.DataFrame(records)

    # --- Leer metadata del modelo directamente desde S3 ---
    s3 = boto3.client("s3")
    response = s3.get_object(
        Bucket="mlflow-models-milk-price-dev", Key="promoted/daily_model.json"
    )
    meta = json.load(response["Body"])

    model_id = meta["artifact_uri"].split("/")[-1]
    model_s3_path = f"s3://mlflow-models-milk-price-dev/2/models/{model_id}/artifacts/"
    model = mlflow.pyfunc.load_model(model_s3_path)

    # --- Generar predicciones ---
    df_pred["Precio_sugerido"] = model.predict(df_pred.to_dict(orient="records"))

    # --- Guardar reporte CSV localmente ---
    output_dir = "reports"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_local_path = f"{output_dir}/predicciones_{fecha_pred}.csv"
    df_pred.to_csv(output_local_path, index=False)
    print(f"✅ Archivo generado: {output_local_path}")

    # --- Subir reporte a S3 ---
    s3_output_key = f"predicciones/{fecha_pred}/predicciones_{fecha_pred}.csv"
    s3.upload_file(
        Filename=output_local_path, Bucket="mlops-milk-datalake", Key=s3_output_key
    )
    print(f"📤 Archivo subido a S3: s3://mlops-milk-datalake/{s3_output_key}")

    return s3_output_key
