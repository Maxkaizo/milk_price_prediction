from prefect import flow
from datetime import datetime
from dateutil.relativedelta import relativedelta

from orchestration.tasks.load_data import load_data
from orchestration.tasks.train_model import train_model
from orchestration.tasks.monitor_data_drift import monitor_data_drift
from orchestration.tasks.monitor_model_drift import monitor_model_drift
from orchestration.tasks.notify_telegram import notify_telegram


@flow(name="main_train_milk_model")
def main(
    source: str = "local",
    year: int = 0,
    month: int = 0
):
    """
    Main flow to load data and train a model monthly.
    If year/month are 0, it uses the previous month as reference.
    """
    if year == 0 or month == 0:
        today = datetime.today()
        reference_date = today - relativedelta(months=1)
        year = reference_date.year
        month = reference_date.month

    print(f"🗓️ Running pipeline for year={year}, month={month}, source={source}")

    # Load data
    X_train_dicts, y_train, X_val_dicts, y_val = load_data(year, month, source)

    # Train model
    rmse, y_pred = train_model(X_train_dicts, y_train, X_val_dicts, y_val)

    # Monitor data drift
    data_drift_dict = monitor_data_drift(
        X_ref_dicts=X_train_dicts,
        y_ref=y_train,
        X_cur_dicts=X_val_dicts,
        y_cur=y_val,
        year=year,
        month=month
    )

    model_drift_dict = monitor_model_drift(
        y_true=y_val,
        y_pred=y_pred,
        year=year,
        month=month
    )

    # Inicio evaluacion para notificacion
    # --- Evaluar Data Drift ---
    try:
        # data_drift_detected = data_drift_dict["metrics"][0]["result"]["dataset_drift"]
        label = data_drift_dict["widgets"][0]["params"]["counters"][0]["label"]
        data_drift_detected = "NOT" not in label.upper()

    except Exception as e:
        data_drift_detected = False
        print("⚠️ No se pudo leer dataset_drift:", e)

    if data_drift_detected:
        notify_telegram.submit("🚨 <b>Data Drift detectado</b>")

    # --- Evaluar Model Drift: cambio de RMSE ---
    try:
        # reported_rmse  = model_drift_dict["metrics"][0]["result"]["rmse"]["value"]
        rmse_str = model_drift_dict["widgets"][4]["params"]["counters"][0]["value"]
        reported_rmse = float(rmse_str)
    except Exception as e:
        reported_rmse  = None
        print("⚠️ No se pudo leer RMSE:", e)

    # Umbral fijo (puedes ajustar esto)
    RMSE_THRESHOLD = 2.0

    if reported_rmse and reported_rmse > RMSE_THRESHOLD:
        notify_telegram.submit(f"⚠️ <b>High RMSE</b>: {reported_rmse :.2f} (> {RMSE_THRESHOLD})")

    # debug posición dato
    # import json

    # with open("model_drift_debug.json", "w") as f:
    #    json.dump(model_drift_dict, f)

    # Fin evaluacion notificación

    print(f"✅ Pipeline completed with RMSE: {rmse:.4f}")
    notify_telegram.submit(f"✅ Pipeline completed with RMSE: {rmse:.4f}")
    return rmse


if __name__ == "__main__":
    main.serve(
        name="train-milk-model",
        cron="0 6 2 * *",  # Día 2 de cada mes a las 6:00 a.m.
        tags=["milk", "training"],
    )