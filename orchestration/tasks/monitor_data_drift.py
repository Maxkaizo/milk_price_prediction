from pathlib import Path
from prefect import task
from evidently import Report
from evidently.presets import DataDriftPreset
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
    df_ref = pd.DataFrame(X_ref_dicts)
    df_ref["Precio"] = y_ref

    df_cur = pd.DataFrame(X_cur_dicts)
    df_cur["Precio"] = y_cur

    report = Report(metrics=[DataDriftPreset()])
    output = report.run(reference_data=df_ref, current_data=df_cur)

    # Carpeta destino
    output_dir = Path("monitor/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Guardamos el reporte en su formato nativo (.evidently.html)
    output_path = output_dir / f"{year}-{month:02d}-data-drift-report.evidently.html"
    output.save_html(str(output_path))

    print(f"📊 Data drift report saved to: {output_path}")

    return output.dump_dict()
