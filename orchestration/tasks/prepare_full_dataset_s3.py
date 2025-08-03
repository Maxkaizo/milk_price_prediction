from prefect import task
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import fsspec


@task(name="prepare_full_dataset_s3")
def prepare_full_dataset_s3(
    reference_date: str = None,  # pass as string in ISO format
    lookback_days: int = 548,
    s3_root: str = "s3://mlops-milk-datalake/daily",
    output_path: str = "data/processed/full_dataset.parquet",
) -> str:
    if reference_date is None:
        reference_date = datetime.today()
    else:
        reference_date = datetime.fromisoformat(reference_date)

    start_date = reference_date - timedelta(days=lookback_days)
    fs = fsspec.filesystem("s3")

    # 1. List all existing Parquet files
    all_paths = fs.glob(f"{s3_root}/**/*-data.parquet")

    # 2. Filter valid files within window
    valid_files = []
    for path in all_paths:
        filename = path.split("/")[-1]
        try:
            file_date = datetime.strptime(
                filename.split("-data.parquet")[0], "%Y-%m-%d"
            )
            if start_date <= file_date <= reference_date:
                valid_files.append(f"s3://{path}")
        except:
            continue

    if not valid_files:
        raise FileNotFoundError("No valid files found within date window.")

    # 3. Load data
    df_list = [pd.read_parquet(fp, filesystem=fs) for fp in sorted(valid_files)]
    df = pd.concat(df_list, ignore_index=True)

    # 4. Preprocessing
    df = df.dropna(subset=["Fecha", "Precio"])
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    group_cols = ["Estado", "Ciudad", "Tipo", "Canal"]
    df = df.sort_values(group_cols + ["Fecha"])
    df["año"] = df["Fecha"].dt.year
    df["mes"] = df["Fecha"].dt.month
    df["dia"] = df["Fecha"].dt.day
    df["dia_semana"] = df["Fecha"].dt.day_name()
    df["Precio_lag1"] = df.groupby(group_cols)["Precio"].shift(1)
    df["Precio_mean7"] = (
        df.groupby(group_cols)["Precio"]
        .rolling(window=7, min_periods=1)
        .mean()
        .reset_index(level=group_cols, drop=True)
    )

    # 5. Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    print(f"✅ Saved {len(df)} rows to: {output_path}")
    return str(output_path)
