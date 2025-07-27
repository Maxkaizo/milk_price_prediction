from prefect import flow
from datetime import datetime
from dateutil.relativedelta import relativedelta

from orchestration.tasks.load_data import load_data
from orchestration.tasks.train_model import train_model
from orchestration.tasks.monitor_data_drift import monitor_data_drift



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
    rmse = train_model(X_train_dicts, y_train, X_val_dicts, y_val)

    # Monitor data drift
    drift_report_path = monitor_data_drift(
        X_ref_dicts=X_train_dicts,
        y_ref=y_train,
        X_cur_dicts=X_val_dicts,
        y_cur=y_val,
        year=year,
        month=month
    )

    print(f"✅ Pipeline completed with RMSE: {rmse:.4f}")
    return rmse


if __name__ == "__main__":
    main.serve(
        name="train-milk-model",
        cron="0 6 2 * *",  # Día 2 de cada mes a las 6:00 a.m.
        tags=["milk", "training"],
    )