# Orchestration with Prefect 3.x

This module contains the flow and tasks for training the milk price prediction model.  
The orchestration is built using **Prefect 3.x**, which brings key changes compared to the previous 2.x model used in the MLOps Zoomcamp course materials.

---

## ⚙️ Why Prefect 3.x?

While following the course, I noticed that Prefect 2.x required:

- Writing `deployment.yaml` and `prefect.yaml` files
- Running `prefect deployment build` and `apply` to register flows
- Setting up work pools and launching dedicated workers
- Managing cron schedules outside the flow logic

In Prefect 3.x, all of this is simplified.

---

## 🚀 What changed in Prefect 3.x?

With Prefect 3.x:

- You register and schedule your flow **inside your code**, using `.serve()`
- There’s **no need** for external YAML files, workers, or pools
- You get a built-in scheduler that runs **as long as the script stays active**

### ✅ Example from this project:

```python
if __name__ == "__main__":
    main.serve(
        name="train-milk-model",
        cron="0 6 2 * *",  # Run on the 2nd day of each month at 6:00am
        tags=["milk", "training"]
    )
```

This single line turns the flow into a live deployment — visible in the Prefect UI and ready to run automatically or manually.

---

## 🧠 Parameter detection in the UI

Prefect 3.x detects your flow parameters automatically:

```python
@flow
def main(source: str = "s3", year: int = 0, month: int = 0):
```

These are exposed in the UI, making it easy to:

* Trigger historical runs (simulated backfills)
* Switch between `local` and `s3` data sources
* Override `year` and `month` values per run

---

## 🧪 Manual backfills

To simulate past runs, you can execute the flow directly:

```bash
python orchestration/flows/main_flow.py
```

Or from Python:

```python
from orchestration.flows.main_flow import main
main(source="s3", year=2023, month=2)
```

This is useful for testing or retraining the model on older data.

---

## 🔁 Multiple deployments from the same flow

Prefect 3.x allows creating **multiple scheduled deployments** from a single flow by calling `.serve()` multiple times:

```python
main.serve(name="monthly-train", cron="0 6 2 * *")
main.serve(name="daily-test", cron="0 8 * * *", parameters={"source": "local"})
```

Each deployment appears in the UI independently, with its own schedule and parameters.

---

## 🖥️ How to run the scheduler

To activate the deployment, run:

```bash
python orchestration/flows/main_flow.py
```

> ⚠️ The process must remain active for the scheduler to work.
> You can use `tmux`, `nohup`, or run it in the background.

---

## ✅ Summary

| Feature                | Prefect 2.x                       | Prefect 3.x              |
| ---------------------- | --------------------------------- | ------------------------ |
| Deployment config      | `deployment.yaml`, `prefect.yaml` | `.serve()` inside Python |
| Scheduling             | Defined outside the flow          | Defined inside the flow  |
| Infrastructure         | Pools + Workers                   | Embedded scheduler       |
| Manual backfills       | Via CLI or API                    | Run from Python directly |
| UI parameter overrides | Limited                           | Automatic and editable   |

---

Using Prefect 3.x allowed me to simplify orchestration in this project, reduce boilerplate, and focus on core logic — while keeping full control from the UI.