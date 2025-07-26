from prefect import flow
from orchestration.tasks.load_data import load_data


@flow
def test_load_data_flow(year: int = 2025, month: int = 7, source: str = "local"):
    """
    Simple Prefect flow to test loading data from local/S3.
    Loads training data for months (M-13 to M-2) and validation data for (M-1).
    """
    X_train, y_train, X_val, y_val = load_data(year=year, month=month, source=source)

    print(f"✅ Loaded {len(X_train)} training samples")
    print(f"✅ Loaded {len(X_val)} validation samples")
    print(f"📊 Training targets: {len(y_train)} | Validation targets: {len(y_val)}")


if __name__ == "__main__":
    test_load_data_flow()
