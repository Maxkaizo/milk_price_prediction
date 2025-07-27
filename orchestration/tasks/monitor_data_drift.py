from pathlib import Path
from prefect import task
from evidently.report import Report
from evidently.metrics import DataDriftPreset
import pandas as pd


@task(name="monitor_data_drift")
def monitor_data_drift(
    X_ref_dicts: list,
    y_ref: list,
    X_cur_dicts: list,
    y_cur: list,
    year: int,
    month: int,
) -> str:
    """
    Generates a data drift report using Evidently, comparing:
    - Reference: all training data (months -13 to -2)
    - Current: validation data (month -1)

    The report is saved as HTML in the `monitor/reports/` folder.

    Args:
        X_ref_dicts (list): List of dicts for reference data (training).
        y_ref (list): List of prices for reference data.
        X_cur_dicts (list): List of dicts for current data (validation).
        y_cur (list): List of prices for current data.
        year (int): Execution year.
        month (int): Execution month.

    Returns:
        str: Path to the generated HTML report.
    """

    # Convert to DataFrames
    df_ref = pd.DataFrame(X_ref_dicts)
    df_ref["Precio"] = y_ref

    df_cur = pd.DataFrame(X_cur_dicts)
    df_cur["Precio"] = y_cur

    # Create Evidently report
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=df_ref, current_data=df_cur)

    # Define output path
    output_dir = Path("monitor/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{year}-{month:02d}-data-drift-report.html"

    report.save_html(str(output_path))
    print(f"📊 Data drift report saved to: {output_path}")

    return str(output_path)
