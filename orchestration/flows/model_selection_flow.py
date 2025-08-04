# milk_price_prediction/orchestration/flows/model_selection_flow.py

from prefect import flow
from orchestration.tasks.notify_telegram import notify_telegram
from training.train_random_forest_model import train_random_forest_model
from training.train_xgboost_model import train_xgboost_model
import mlflow


@flow(name="train_and_select_model")
def train_and_select_model_flow():
    notify_telegram.send("🚀 Starting model training and selection pipeline...")

    # Run both training tasks
    rmse_rf = train_random_forest_model()
    rmse_xgb = train_xgboost_model()

    # Decision logic: lower RMSE is better
    if rmse_rf < rmse_xgb:
        best_model_name = "milk-price-predictor-rf"
        notify_telegram.send(f"✅ Best model is Random Forest with RMSE: {rmse_rf:.4f}")
    else:
        best_model_name = "milk-price-predictor-xgb"
        notify_telegram.send(f"✅ Best model is XGBoost with RMSE: {rmse_xgb:.4f}")

    # Promote best model to Staging
    client = mlflow.MlflowClient()
    versions = client.get_latest_versions(best_model_name, stages=["None"])

    if versions:
        model_version = versions[0].version
        client.transition_model_version_stage(
            name=best_model_name,
            version=model_version,
            stage="Staging",
            archive_existing_versions=True,
        )
        notify_telegram.send(
            f"📌 Promoted model '{best_model_name}' version {model_version} to 'Staging' in MLflow."
        )
    else:
        notify_telegram.send(
            f"⚠️ No version found to promote for model '{best_model_name}'"
        )


if __name__ == "__main__":
    train_and_select_model_flow()
