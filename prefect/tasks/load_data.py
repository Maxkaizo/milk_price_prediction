from pathlib import Path
from prefect import task
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta


def read_parquet_partition(year: int, month: int, source: str = "local") -> pd.DataFrame:
    """
    Reads a single monthly .parquet file from local or S3.

    Expected file structure:
    - Local: data/datalake/monthly/YYYY/MM/YYYY-MM-data.parquet
    - S3:    s3://bucket/monthly/YYYY/MM/YYYY-MM-data.parquet
    """
    filename = f"{year}-{month:02d}-data.parquet"
    file_path = f"monthly/{year}/{month:02d}/{filename}"

    if source == "s3":
        bucket = os.getenv("S3_BUCKET", "mlops-milk-datalake")
        s3_uri = f"s3://{bucket}/{file_path}"
        print(f"📡 Loading from S3: {s3_uri}")
        return pd.read_parquet(s3_uri, storage_options={"anon": True})
    else:
        local_path = Path("data/datalake") / file_path
        print(f"📁 Loading from local: {local_path}")
        return pd.read_parquet(local_path)


@task
def load_data(year: int, month: int, source: str = "local"):
    """
    Loads training and validation data using a sliding window.

    - Training: from (month - 13) to (month - 2)
    - Validation: (month - 1)

    Args:
        year (int): current reference year (training runs at the beginning of this month)
        month (int): current reference month
        source (str): "local" or "s3"

    Returns:
        tuple: (X_train_dicts, y_train, X_val_dicts, y_val)
    """
    categorical = ["Estado", "Ciudad", "Tipo", "Canal"]
    X_train_dicts = []
    y_train = []

    # Training: months 13 to 2 before the reference month
    train_months = [
        (datetime(year, month, 1) - relativedelta(months=i)).date()
        for i in range(13, 1, -1)
    ]

    for date in train_months:
        df = read_parquet_partition(date.year, date.month, source)
        df = df.dropna(subset=["Precio"])
        df[categorical] = df[categorical].astype(str)

        feature_dicts = df[categorical].to_dict(orient="records")
        X_train_dicts.extend(feature_dicts)
        y_train.extend(df["Precio"].values)

    # Validation: previous month
    val_date = datetime(year, month, 1) - relativedelta(months=1)
    df_val = read_parquet_partition(val_date.year, val_date.month, source)
    df_val = df_val.dropna(subset=["Precio"])
    df_val[categorical] = df_val[categorical].astype(str)

    X_val_dicts = df_val[categorical].to_dict(orient="records")
    y_val = df_val["Precio"].values

    return X_train_dicts, y_train, X_val_dicts, y_val
