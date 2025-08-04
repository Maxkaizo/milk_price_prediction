import pandas as pd
from pathlib import Path
from prefect import task
from evidently import Report, Dataset, Regression, DataDefinition
from evidently.metrics import MeanError, RMSE, DummyMAE, DummyRMSE


@task(name="monitor_model_drift")
def monitor_model_drift(
    y_true: list,
    y_pred: list,
    year: int,
    month: int,
) -> str:
    curr_df = pd.DataFrame({"prediction": y_pred, "target": y_true})

    data_definition = DataDefinition(
        regression=[Regression(target="target", prediction="prediction")]
    )

    curr_dataset = Dataset.from_pandas(curr_df, data_definition=data_definition)

    report = Report([MeanError(), RMSE(), DummyMAE(), DummyRMSE()])

    output = report.run(current_data=curr_dataset)

    output_dir = Path("monitor/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{year}-{month:02d}-model-drift-report_.html"
    output.save_html(str(output_path))

    print(f"📉 Model drift report saved to: {output_path}")

    return output.dump_dict()
