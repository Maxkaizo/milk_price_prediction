from prefect import flow
from datetime import datetime
from orchestration.tasks.check_file_availability import check_file_availability
from orchestration.tasks.extract_and_ingest_today import extract_and_ingest_today
from orchestration.tasks.monitor_data_drift_from_s3 import monitor_data_drift_from_s3
from orchestration.tasks.notify_telegram import notify_telegram
from orchestration.tasks.prepare_full_dataset_s3 import prepare_full_dataset_s3
from orchestration.tasks.train_random_forest_model import train_random_forest_model
from orchestration.tasks.train_xgboost_model import train_xgboost_model
import mlflow
from typing import Optional

import boto3
import json


@flow(name="daily-mlops-pipeline")
def daily_pipeline(execution_date: Optional[str] = None):
    # Parse date
    if execution_date is None:
        exec_date = datetime.today()
    else:
        exec_date = datetime.fromisoformat(execution_date)

    # Step 1: Check if new file is available
    should_run = check_file_availability(execution_date=exec_date)
    notify_telegram.submit("✅ Checked file availability.")

    if not should_run:
        print("🚫 No new file to process.")
        notify_telegram.submit("🚫 No new file to process.")
        return

    # Step 2: Extract and ingest data
    s3_path = extract_and_ingest_today(execution_date=exec_date)
    print(f"✅ File ingested and uploaded to: {s3_path}")
    notify_telegram.submit(f"✅ File ingested: {s3_path}")

    # Step 3: Data Drift Monitoring
    drift_report = monitor_data_drift_from_s3()
    print("📈 Drift monitoring complete.")
    notify_telegram.submit("📈 Drift monitoring complete.")

    try:
        label = drift_report["widgets"][0]["params"]["counters"][0]["label"]
        data_drift_detected = "NOT" not in label.upper()
    except Exception as e:
        data_drift_detected = False
        print("⚠️ Couldn't determine data drift status:", e)

    if data_drift_detected:
        notify_telegram.submit("🚨 <b>Data Drift detected</b>")
    else:
        notify_telegram.submit("✅ <b>Data drift evaluated, and no issues found</b>")

    # Step 4: Prepare dataset for training
    output_path = prepare_full_dataset_s3(reference_date=str(exec_date))
    print(f"📦 Full dataset prepared at: {output_path}")
    notify_telegram.submit(f"📦 Full dataset ready: {output_path}")

    # Step 5: Train models
    notify_telegram.submit("🚀 Starting model training and selection pipeline...")
    rmse_rf = train_random_forest_model()
    notify_telegram.submit(f"🌲 Random Forest trained with RMSE: {rmse_rf:.4f}")
    rmse_xgb = train_xgboost_model()
    notify_telegram.submit(f"⚡ XGBoost trained with RMSE: {rmse_xgb:.4f}")

    # Step 6: Choose best model
    if rmse_rf < rmse_xgb:
        best_model_name = "milk-price-predictor-rf"
        best_rmse = rmse_rf
        notify_telegram.submit(f"✅ Best model: Random Forest (RMSE: {rmse_rf:.4f})")
    else:
        best_model_name = "milk-price-predictor-xgb"
        best_rmse = rmse_xgb
        notify_telegram.submit(f"✅ Best model: XGBoost (RMSE: {rmse_xgb:.4f})")

    # Step 7: Promote best model to Staging and save metadata to S3
    client = mlflow.MlflowClient()
    versions = client.get_latest_versions(best_model_name, stages=["None"])

    if versions:
        model_version = versions[0].version
        run_id = versions[0].run_id

        # Promote to Staging
        client.transition_model_version_stage(
            name=best_model_name,
            version=model_version,
            stage="Staging",
            archive_existing_versions=True,
        )

        # Get registered model version info (model_id path)
        registered_model = client.get_model_version(
            name=best_model_name, version=model_version
        )

        artifact_uri = registered_model.source  # ✅ this is the correct S3 model path

        run = client.get_run(run_id)
        rmse = float(run.data.metrics.get("final_rmse", best_rmse))

        # Save promotion metadata to S3
        promotion_record = {
            "model_name": best_model_name,
            "version": str(model_version),
            "run_id": run_id,
            "artifact_uri": artifact_uri,
            "rmse": rmse,
            "promoted_stage": "Staging",
            "promotion_time": datetime.utcnow().isoformat(),
        }

        s3 = boto3.client("s3")
        s3.put_object(
            Bucket="mlflow-models-milk-price-dev",
            Key="promoted/daily_model.json",
            Body=json.dumps(promotion_record),
            ContentType="application/json",
        )

        print("📤 Promotion metadata saved to S3.")
        notify_telegram.submit(
            f"📌 Promoted '{best_model_name}' v{model_version} to <b>Staging</b> and saved metadata to S3."
        )
    else:
        notify_telegram.submit(
            f"⚠️ No version found to promote for model '{best_model_name}'"
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        execution_date = sys.argv[1]
        daily_pipeline(execution_date=execution_date)
    else:
        daily_pipeline()

    # Serve deployment for Prefect UI with daily schedule at 1 PM (Mexico City time)
    daily_pipeline.serve(
        name="daily-milk-predictor",
        cron="0 13 * * *",  # 1 PM UTC-6 (CDMX), ajusta si tu Prefect está en UTC
        tags=["milk", "batch", "training"],
        description="Daily training pipeline for milk price prediction at 1 PM",
    )