import boto3


def test_s3_connection(bucket_name):
    s3 = boto3.client("s3")

    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        print(f"✅ Conexión exitosa a S3. Objetos en '{bucket_name}':")
        for obj in response.get("Contents", []):
            print(" -", obj["Key"])
    except s3.exceptions.NoSuchBucket:
        print(f"❌ El bucket '{bucket_name}' no existe.")
    except Exception as e:
        print("❌ Error general:", e)


if __name__ == "__main__":
    test_s3_connection("mlflow-models-milk-price-dev")
