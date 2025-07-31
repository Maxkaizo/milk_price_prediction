# milk_price_prediction/training/train_xgboost_model.py

# ✅ Objective: Train an XGBoost model with Hyperopt using a pipeline that includes DictVectorizer.
# The trained model is logged and registered in MLflow.

import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
import mlflow
import mlflow.sklearn
from datetime import datetime
from prefect import task

@task(name="train_xgboost_model")
def train_xgboost_model(path_to_dataset: str = "data/processed/full_dataset.parquet", max_evals: int = 25):
    df = pd.read_parquet(path_to_dataset)
    df = df.dropna(subset=["Precio", "Precio_lag1", "Precio_mean7"])

    categorical = ["Estado", "Ciudad", "Tipo", "Canal", "dia_semana"]
    numerical = ["Precio_lag1", "Precio_mean7", "mes", "dia", "año"]
    df[categorical] = df[categorical].astype(str)

    feature_dicts = df[categorical + numerical].to_dict(orient="records")
    y = df["Precio"].values

    def objective_xgb(params):
        with mlflow.start_run(nested=True):
            mlflow.log_params(params)
            mlflow.set_tags({"model_type": "xgboost"})

            pipeline = Pipeline([
                ("vectorizer", DictVectorizer()),
                ("regressor", XGBRegressor(
                    max_depth=int(params["max_depth"]),
                    learning_rate=params["learning_rate"],
                    n_estimators=int(params["n_estimators"]),
                    min_child_weight=params["min_child_weight"],
                    gamma=params["gamma"],
                    subsample=params["subsample"],
                    colsample_bytree=params["colsample_bytree"] ,
                    random_state=42,
                    n_jobs=-1
                ))
            ])

            score = cross_val_score(pipeline, feature_dicts, y, scoring="neg_root_mean_squared_error", cv=3)
            rmse = -score.mean()
            mlflow.log_metric("rmse", rmse)
            return {"loss": rmse, "status": STATUS_OK}

    search_space_xgb = {
        "max_depth": hp.quniform("max_depth", 3, 10, 1),
        "learning_rate": hp.loguniform("learning_rate", -4, 0),
        "n_estimators": hp.quniform("n_estimators", 50, 300, 10),
        "min_child_weight": hp.quniform("min_child_weight", 1, 10, 1),
        "gamma": hp.uniform("gamma", 0, 1),
        "subsample": hp.uniform("subsample", 0.5, 1.0),
        "colsample_bytree": hp.uniform("colsample_bytree", 0.5, 1.0),
    }

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("milk-price-predictor")

    run_date = datetime.today()
    run_name = f"xgb-milk-predictor-{run_date.year}-{run_date.month:02d}"
    model_name = "milk-price-predictor-xgb"

    with mlflow.start_run(run_name=run_name) as run:
        trials_xgb = Trials()
        best_xgb = fmin(fn=objective_xgb, space=search_space_xgb, algo=tpe.suggest, max_evals=max_evals, trials=trials_xgb)

        dv = DictVectorizer()
        X = dv.fit_transform(feature_dicts)

        final_xgb = XGBRegressor(
            max_depth=int(best_xgb["max_depth"]),
            learning_rate=best_xgb["learning_rate"],
            n_estimators=int(best_xgb["n_estimators"]),
            min_child_weight=best_xgb["min_child_weight"],
            gamma=best_xgb["gamma"],
            subsample=best_xgb["subsample"],
            colsample_bytree=best_xgb["colsample_bytree"],
            random_state=42,
            n_jobs=-1
        )

        pipeline = Pipeline([
            ("vectorizer", dv),
            ("regressor", final_xgb)
        ])
        pipeline.fit(feature_dicts, y)
        y_pred = pipeline.predict(feature_dicts)
        rmse = root_mean_squared_error(y, y_pred)

        mlflow.log_metric("final_rmse", rmse)
        mlflow.set_tags({"model_type": "xgboost"})
        mlflow.sklearn.log_model(pipeline, artifact_path="model")

        run_id = run.info.run_id
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri=model_uri, name=model_name)

        print(f"✅ Final RMSE XGBoost: {rmse:.4f}")
        print(f"📌 Model logged to MLflow with run ID: {run_id}")
        print(f"📌 Model registered in MLflow Model Registry as '{model_name}'")

        return rmse