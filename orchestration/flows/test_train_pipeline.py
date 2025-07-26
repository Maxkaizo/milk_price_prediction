from orchestration.tasks.load_data import load_data
from orchestration.tasks.train_model import train_model
from prefect import flow

@flow
def train_pipeline(year: int, month: int, source: str = "local"):
    X_train_dicts, y_train, X_val_dicts, y_val = load_data(year, month, source)
    train_model(X_train_dicts, y_train, X_val_dicts, y_val)

if __name__ == "__main__":
    train_pipeline(year=2025, month=7)
