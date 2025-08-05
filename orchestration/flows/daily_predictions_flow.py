from prefect import flow
from orchestration.tasks.generate_daily_predictions import generate_daily_predictions
from orchestration.tasks.notify_telegram import notify_telegram
from datetime import datetime


@flow(name="daily_prediction_flow_batch")
def daily_prediction_flow():
    """
    Este flujo genera predicciones de precios de leche para el día siguiente.
    Carga el modelo desde S3, arma los features y guarda los resultados en otro bucket S3.
    """
    fecha = datetime.today().date()
    notify_telegram.submit(f"📈 Starting daily prediction for {fecha}")

    try:
        s3_path = generate_daily_predictions()
        notify_telegram.submit(f"✅ Daily prediction uploaded to: {s3_path}")
    except Exception as e:
        notify_telegram.submit(f"❌ Error during daily prediction: {str(e)}")
        raise

    return s3_path


if __name__ == "__main__":
    daily_prediction_flow.serve(
        name="daily-milk-batch",
        cron="0 23 * * *",  # Todos los días a las 11 PM
        tags=["milk", "batch", "prediction"],
    )
