import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://localhost:5000")


# Nombre del modelo tal como aparece en el registry
MODEL_NAME = "milk-price-predictor"

client = MlflowClient()
latest_version = client.get_latest_versions(MODEL_NAME, stages=[])[-1].version

# Ejemplo de entrada (debe coincidir con los features usados al entrenar)
sample_input = {
    "Estado": "Jalisco",
    "Ciudad": "Guadalajara",
    "Tipo": "Leche pasteurizada",
    "Canal": "Autoservicio"
}

if __name__ == "__main__":
    # Ruta al modelo específico por versión
    model_uri = f"models:/{MODEL_NAME}/{latest_version}"

    # Cargar modelo registrado
    model = mlflow.pyfunc.load_model(model_uri)

    # Crear DataFrame desde el input
    # df = pd.DataFrame([sample_input])
    df = [sample_input]  # lista de un solo diccionario


    # Realizar predicción
    pred = model.predict(df)

    print(f"✅ Entrada: {sample_input}")
    print(f"➡️ Predicción de precio: ${pred[0]:.2f}")
