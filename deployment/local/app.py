from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

# Carga el modelo entrenado
with open("model/model.pkl", "rb") as f_in:
    model = pickle.load(f_in)

@app.route("/predict", methods=["POST"])
def predict():
    features = request.get_json()

    # Asegúrate que la entrada sea una lista de diccionarios
    if isinstance(features, dict):
        features = [features]

    try:
        prediction = model.predict(features)
        return jsonify({"predicted_price": float(prediction[0])})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)

