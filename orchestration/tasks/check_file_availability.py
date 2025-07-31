# tasks/check_file_availability.py

from datetime import datetime
import boto3
import requests
from prefect import task

BUCKET_NAME = "mlops-milk-datalake"
S3_PREFIX = "daily"
BASE_URL = "https://www.economia-sniim.gob.mx/SNIIM-Archivosfuente/Comentarios/Otros"

@task
def check_file_availability():
    today = datetime.today()
    excel_filename = f"Leche{today.strftime('%d%m%Y')}.xlsx"
    parquet_filename = f"{today.strftime('%Y-%m-%d')}-data.parquet"
    s3_key = f"{S3_PREFIX}/{today.year}/{today.strftime('%m')}/{parquet_filename}"

    s3 = boto3.client("s3")

    def s3_file_exists(bucket: str, key: str) -> bool:
        try:
            s3.head_object(Bucket=bucket, Key=key)
            return True
        except s3.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise

    def remote_file_exists(url: str) -> bool:
        response = requests.head(url)
        return response.status_code == 200

    file_in_s3 = s3_file_exists(BUCKET_NAME, s3_key)
    file_online = remote_file_exists(f"{BASE_URL}/{excel_filename}")
    return not file_in_s3 and file_online
