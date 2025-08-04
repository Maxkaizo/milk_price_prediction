from flask import Flask, request, jsonify
import mlflow.pyfunc
import json
import boto3

# --- Load model metadata directly from S3 ---
s3 = boto3.client("s3")
response = s3.get_object(
    Bucket="mlflow-models-milk-price-dev", Key="promoted/daily_model.json"
)
meta = json.load(response["Body"])

model_id = meta["artifact_uri"].split("/")[-1]
model_s3_path = f"s3://mlflow-models-milk-price-dev/2/models/{model_id}/artifacts/"
model = mlflow.pyfunc.load_model(model_s3_path)

# --- Initialize Flask app ---
app = Flask(__name__)


@app.route("/predict", methods=["POST"])
def predict():
    features = request.get_json()

    # Ensure input is a list of dictionaries
    if isinstance(features, dict):
        features = [features]

    try:
        prediction = model.predict(features)
        return jsonify({"predicted_price": float(prediction[0])})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/", methods=["GET"])
def health():
    return "App is running", 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
