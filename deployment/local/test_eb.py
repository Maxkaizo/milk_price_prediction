import requests

sample = {
    "Estado": "Jalisco",
    "Ciudad": "Guadalajara",
    "Tipo": "Leche pasteurizada",
    "Canal": "Autoservicio"
}

res = requests.post(
    "http://milk-price-env.eba-jzbnyzpp.us-west-2.elasticbeanstalk.com/predict",
    json=sample
)

print(res.status_code, res.json())
