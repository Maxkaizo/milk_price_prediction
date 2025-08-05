import requests

url = "http://localhost:9696/predict"

sample_input = {
    "Estado": "Jalisco",
    "Ciudad": "Guadalajara",
    "Tipo": "Leche pasteurizada",
    "Canal": "Autoservicio",
}

response = requests.post(url, json=sample_input)
print("Predicted price:", response.json())
