import json
import boto3
import mlflow.pyfunc

s3 = boto3.client("s3")
response = s3.get_object(
    Bucket="mlflow-models-milk-price-dev",
    Key="promoted/daily_model.json"
)
meta = json.load(response["Body"])

model_id = meta["artifact_uri"].split("/")[-1]
model_s3_path = f"s3://mlflow-models-milk-price-dev/2/models/{model_id}/artifacts/"
model = mlflow.pyfunc.load_model(model_s3_path)

# Lambda handler
def handler(event, context):

    try:

        raw_body = event.get('body')

        if isinstance(raw_body, str):
            body = json.loads(raw_body)
        else:
            body = raw_body if raw_body is not None else event

        if isinstance(body, dict):
            body = [body]

        prediction = model.predict(body)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"   
            },
            "body": json.dumps({"predicted_price": float(prediction[0])})
        }

    except Exception as e:
        print(f"[ERROR] Ha ocurrido una excepción: {e}")
        
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": str(e)})
        }