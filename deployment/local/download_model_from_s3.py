import boto3
from pathlib import Path

BUCKET_NAME = "mlflow-models-milk-price-dev"
LOCAL_MODEL_PATH = Path("model/model.pkl")
MODEL_FILENAME = "model.pkl"


def download_latest_model():
    s3 = boto3.client("s3")

    # Listar todos los objetos en el bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    if "Contents" not in response:
        raise RuntimeError("No files found in bucket.")

    # Filtrar solo los model.pkl
    model_files = [
        obj for obj in response["Contents"] if obj["Key"].endswith(MODEL_FILENAME)
    ]

    if not model_files:
        raise RuntimeError("No model.pkl files found in bucket.")

    # Seleccionar el archivo más reciente
    latest_file = max(model_files, key=lambda x: x["LastModified"])

    print(
        f"📦 Found latest model: {latest_file['Key']} ({latest_file['LastModified']})"
    )

    # Crear carpeta local si no existe
    LOCAL_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Descargar el archivo
    s3.download_file(BUCKET_NAME, latest_file["Key"], str(LOCAL_MODEL_PATH))

    print(f"✅ Model downloaded to: {LOCAL_MODEL_PATH}")


if __name__ == "__main__":
    download_latest_model()
