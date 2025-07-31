# milk_price_prediction/training/train_random_forest_model.py

# ✅ Objective: Train a Random Forest model with Hyperopt using a pipeline that includes DictVectorizer.
# The trained model is logged and registered in MLflow.

import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
import mlflow
import mlflow.sklearn
from datetime import datetime
from prefect import task

@task(name="train_random_forest_model")
def train_random_forest_model(path_to_dataset: str = "data/processed/full_dataset.parquet", max_evals: int = 25):
    df = pd.read_parquet(path_to_dataset)
    df = df.dropna(subset=["Precio", "Precio_lag1", "Precio_mean7"])

    categorical = ["Estado", "Ciudad", "Tipo", "Canal", "dia_semana"]
    numerical = ["Precio_lag1", "Precio_mean7", "mes", "dia", "año"]
    df[categorical] = df[categorical].astype(str)

    feature_dicts = df[categorical + numerical].to_dict(orient="records")
    y = df["Precio"].values

    def objective_rf(params):
        with mlflow.start_run(nested=True):
            mlflow.log_params(params)
            mlflow.set_tags({"model_type": "random_forest"})

            pipeline = Pipeline([
                ("vectorizer", DictVectorizer()),
                ("regressor", RandomForestRegressor(
                    n_estimators=int(params["n_estimators"]),
                    max_depth=int(params["max_depth"]),
                    min_samples_split=int(params["min_samples_split"]),
                    min_samples_leaf=int(params["min_samples_leaf"]),
                    random_state=42,
                    n_jobs=-1
                ))
            ])

            score = cross_val_score(pipeline, feature_dicts, y, scoring="neg_root_mean_squared_error", cv=3)
            rmse = -score.mean()
            mlflow.log_metric("rmse", rmse)
            return {"loss": rmse, "status": STATUS_OK}

    search_space_rf = {
        "n_estimators": hp.quniform("n_estimators", 50, 300, 10),
        "max_depth": hp.quniform("max_depth", 5, 20, 1),
        "min_samples_split": hp.quniform("min_samples_split", 2, 10, 1),
        "min_samples_leaf": hp.quniform("min_samples_leaf", 1, 5, 1)
    }

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("milk-price-predictor")

    run_date = datetime.today()
    run_name = f"rf-milk-predictor-{run_date.year}-{run_date.month:02d}"
    model_name = "milk-price-predictor-rf"

    with mlflow.start_run(run_name=run_name) as run:
        trials_rf = Trials()
        best_rf = fmin(fn=objective_rf, space=search_space_rf, algo=tpe.suggest, max_evals=max_evals, trials=trials_rf)

        dv = DictVectorizer()
        X = dv.fit_transform(feature_dicts)

        final_rf = RandomForestRegressor(
            n_estimators=int(best_rf["n_estimators"]),
            max_depth=int(best_rf["max_depth"]),
            min_samples_split=int(best_rf["min_samples_split"]),
            min_samples_leaf=int(best_rf["min_samples_leaf"]),
            random_state=42,
            n_jobs=-1
        )

        pipeline = Pipeline([
            ("vectorizer", dv),
            ("regressor", final_rf)
        ])
        pipeline.fit(feature_dicts, y)
        y_pred = pipeline.predict(feature_dicts)
        rmse = root_mean_squared_error(y, y_pred)

        mlflow.log_metric("final_rmse", rmse)
        mlflow.set_tags({"model_type": "random_forest"})
        mlflow.sklearn.log_model(pipeline, artifact_path="model")

        run_id = run.info.run_id
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri=model_uri, name=model_name)

        print(f"✅ Final RMSE Random Forest: {rmse:.4f}")
        print(f"📌 Model logged to MLflow with run ID: {run_id}")
        print(f"📌 Model registered in MLflow Model Registry as '{model_name}'")

        return rmse
