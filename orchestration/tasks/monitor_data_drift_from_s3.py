from pathlib import Path
from datetime import datetime, timedelta
from prefect import task
from evidently import Report
from evidently.presets import DataDriftPreset
import pandas as pd
import s3fs


@task(name="monitor_data_drift_from_s3")
def monitor_data_drift_from_s3(
    bucket: str = "mlops-milk-datalake",
    prefix: str = "daily/",
    current_days: int = 30,
    reference_days: int = 180,
    execution_date: datetime = None,
) -> str:
    # --- Set up S3 FS ---
    fs = s3fs.S3FileSystem()

    # --- List all relevant parquet files ---
    all_files = fs.glob(f"{bucket}/{prefix}**/*.parquet")

    # --- Convert S3 keys to datetime ---
    def extract_date_from_key(key: str) -> datetime:
        parts = key.split("/")
        filename = parts[-1]
        date_str = filename.split("-data.parquet")[0]
        return datetime.strptime(date_str, "%Y-%m-%d")

    dated_files = [
        (key, extract_date_from_key(key))
        for key in all_files
        if key.endswith(".parquet")
    ]

    # --- Determine date anchors ---
    base_date = execution_date or datetime.today()
    base_date = base_date.replace(hour=0, minute=0, second=0, microsecond=0)

    current_cutoff = base_date - timedelta(days=current_days)
    reference_cutoff = current_cutoff - timedelta(days=reference_days)

    # --- Sort and split into current and reference windows ---
    dated_files.sort(key=lambda x: x[1], reverse=True)

    current_files = [f for f, d in dated_files if d >= current_cutoff]
    reference_files = [
        f for f, d in dated_files if reference_cutoff <= d < current_cutoff
    ]

    if not current_files or not reference_files:
        raise ValueError("❌ Not enough files to compute drift report.")

    print(f"📁 Current files: {len(current_files)}")
    print(f"📁 Reference files: {len(reference_files)}")

    # --- Load data ---
    df_cur = pd.concat(
        [
            pd.read_parquet(f"s3://{f}", storage_options={"anon": False})
            for f in current_files
        ]
    )
    df_ref = pd.concat(
        [
            pd.read_parquet(f"s3://{f}", storage_options={"anon": False})
            for f in reference_files
        ]
    )

    df_cur["Fecha"] = pd.to_datetime(df_cur["Fecha"])
    df_ref["Fecha"] = pd.to_datetime(df_ref["Fecha"])

    # --- Run Report ---
    report = Report(metrics=[DataDriftPreset()])
    output = report.run(reference_data=df_ref, current_data=df_cur)

    # --- Save HTML Report ---
    output_dir = Path("monitor/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = (
        output_dir
        / f"{base_date.strftime('%Y-%m-%d')}-data-drift-report.evidently.html"
    )
    output.save_html(str(output_path))

    print(f"📊 Drift report saved: {output_path}")

    return output.dump_dict()
