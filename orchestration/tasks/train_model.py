from prefect import task
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import cross_val_score
from xgboost import XGBRegressor
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
import mlflow
import mlflow.sklearn
from datetime import datetime

@task
def train_model(X_train_dicts, y_train, X_val_dicts, y_val, model_name="milk-price-predictor", max_evals=25):
    """
    Performs hyperparameter tuning using Hyperopt, trains final model, logs to MLflow, and registers the model.
    """
    run_date = datetime.today()

    # MLflow config
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("milk-price-xgboost-pipeline")

    search_space = {
        "max_depth": hp.quniform("max_depth", 3, 10, 1),
        "learning_rate": hp.loguniform("learning_rate", -4, 0),
        "n_estimators": hp.quniform("n_estimators", 50, 300, 10),
        "min_child_weight": hp.quniform("min_child_weight", 1, 10, 1),
        "gamma": hp.uniform("gamma", 0, 1),
        "subsample": hp.uniform("subsample", 0.5, 1.0),
        "colsample_bytree": hp.uniform("colsample_bytree", 0.5, 1.0),
    }

    def objective(params):
        with mlflow.start_run(nested=True):
            mlflow.log_params(params)

            model = XGBRegressor(
                max_depth=int(params["max_depth"]),
                learning_rate=params["learning_rate"],
                n_estimators=int(params["n_estimators"]),
                min_child_weight=params["min_child_weight"],
                gamma=params["gamma"],
                subsample=params["subsample"],
                colsample_bytree=params["colsample_bytree"],
                random_state=42,
                n_jobs=-1
            )

            pipeline = Pipeline([
                ("vectorizer", DictVectorizer()),
                ("regressor", model)
            ])

            score = cross_val_score(
                pipeline, X_train_dicts, y_train,
                scoring="neg_root_mean_squared_error",
                cv=3
            )
            rmse = -score.mean()
            mlflow.log_metric("rmse", rmse)
            return {"loss": rmse, "status": STATUS_OK}

    run_name = f"xgb-milk-predictor-{run_date.year}-{run_date.month:02d}"

    with mlflow.start_run(run_name=run_name) as active_run:
        trials = Trials()
        best = fmin(
            fn=objective,
            space=search_space,
            algo=tpe.suggest,
            max_evals=max_evals,
            trials=trials,
        )

        best_model = XGBRegressor(
            max_depth=int(best["max_depth"]),
            learning_rate=best["learning_rate"],
            n_estimators=int(best["n_estimators"]),
            min_child_weight=best["min_child_weight"],
            gamma=best["gamma"],
            subsample=best["subsample"],
            colsample_bytree=best["colsample_bytree"],
            random_state=42,
            n_jobs=-1
        )

        pipeline = Pipeline([
            ("vectorizer", DictVectorizer()),
            ("regressor", best_model)
        ])

        pipeline.fit(X_train_dicts, y_train)
        y_pred = pipeline.predict(X_val_dicts)
        rmse = root_mean_squared_error(y_val, y_pred)

        mlflow.log_metric("final_val_rmse", rmse)
        mlflow.sklearn.log_model(pipeline, artifact_path="model")

        # Register model
        run_id = active_run.info.run_id
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri=model_uri, name=model_name)

        print(f"✅ Final RMSE on validation set: {rmse:.4f}")
        print(f"📌 Model registered in MLflow Model Registry as '{model_name}'")

        return rmse, y_pred.tolist()
