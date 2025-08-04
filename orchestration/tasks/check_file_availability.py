# orchestration/tasks/check_file_availability.py

from datetime import datetime
import boto3
import requests
from prefect import task

BUCKET_NAME = "mlops-milk-datalake"
S3_PREFIX = "daily"
BASE_URL = "https://www.economia-sniim.gob.mx/SNIIM-Archivosfuente/Comentarios/Otros"


def build_filenames(execution_date: datetime):
    """
    Helper para construir los nombres y rutas del archivo Excel y Parquet.
    """
    excel_filename = f"Leche{execution_date.strftime('%d%m%Y')}.xlsx"
    parquet_filename = f"{execution_date.strftime('%Y-%m-%d')}-data.parquet"
    s3_key = f"{S3_PREFIX}/{execution_date.year}/{execution_date.strftime('%m')}/{parquet_filename}"
    return excel_filename, s3_key


def _is_file_available_logic(execution_date: datetime) -> bool:
    """
    Lógica pura para decidir si vale la pena correr el flujo:
    Solo si el archivo .xlsx existe en línea y no ha sido cargado en S3.
    """
    excel_filename, s3_key = build_filenames(execution_date)

    # Consulta S3
    s3 = boto3.client("s3")
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        file_in_s3 = True
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            file_in_s3 = False
        else:
            raise

    # Consulta web
    response = requests.head(f"{BASE_URL}/{excel_filename}")
    file_online = response.status_code == 200

    return not file_in_s3 and file_online


@task
def check_file_availability(execution_date: datetime = None) -> bool:
    """
    Tarea de Prefect que llama la lógica base.
    """
    execution_date = execution_date or datetime.today()
    return _is_file_available_logic(execution_date)
