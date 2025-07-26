import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://localhost:5000")

# Nombre del modelo tal como aparece en el registry
MODEL_NAME = "milk-price-predictor"

client = MlflowClient()
latest_version = client.get_latest_versions(MODEL_NAME, stages=[])[-1]

# Extra: detalles del modelo
model_details = client.get_model_version(name=MODEL_NAME, version=latest_version.version)

# Ejemplo de entrada (debe coincidir con los features usados al entrenar)
sample_input = {
    "Estado": "Jalisco",
    "Ciudad": "Guadalajara",
    "Tipo": "Leche pasteurizada",
    "Canal": "Autoservicio"
}

if __name__ == "__main__":
    # Ruta al modelo específico por versión
    model_uri = f"models:/{MODEL_NAME}/{latest_version.version}"

    # Cargar modelo registrado
    model = mlflow.pyfunc.load_model(model_uri)

    # Crear input como lista de diccionario (usado por DictVectorizer)
    df = [sample_input]

    # Realizar predicción
    pred = model.predict(df)

    print("========== MODEL INFO ==========")
    print(f"📦 Model name: {MODEL_NAME}")
    print(f"🔢 Version: {model_details.version}")
    print(f"🆔 Run ID: {model_details.run_id}")
    print(f"📅 Created at: {model_details.creation_timestamp}")
    print(f"📍 Source: {model_details.source}")
    print(f"📂 Artifact path: {model_details.source.split('/')[-2]}")
    print(f"✅ Stage: {model_details.current_stage or 'Not assigned'}")

    print("\n========== PREDICTION ==========")
    print(f"🧾 Input: {sample_input}")
    print(f"💰 Predicted price: ${pred[0]:.2f}")
