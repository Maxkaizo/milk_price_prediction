# Roadmap:

* Entirely Local. Local files + Flask
* Entirely Local + gunicorn
* Local with Docker container + gunicorn
* Cloud deployment using Elastic Beanstalk (with Docker image)
* Cloud deployment in steaming mode. Using Lambda + Kinesis --- configurar manualmente la lambda
* Cloud deployment in steaming mode. Using Lambda + Kinesis + ECR --- crear la lambda a partir de un contenedor docker, a partir de aqui ya descargaremos el modelo del bucket de s3 mas reciente 
* Cloud deployment in steaming mode. Using Lambda + Kinesis + ECR + Terraform, managed via Terraform


# Completed:

## Entirely local

- Use a previously trained model, stored locally
- Run a Flask Server
- predict using curl

![alt text](../images/image.png)

![alt text](../images/curl.png)

## Entirely local + gunicorn

- Switched to gunicorn

![alt text](../images/gunicorn.png)

![alt text](../images/curl_gunicorn.png)

## Local with Docker container + gunicorn

- Built container

![alt text](../images/container_gunicorn.png)

![alt text](../images/curl3.png)

## Cloud deployment using Elastic Beanstalk (with Docker image)

- Deployed with AWS eb cli

![alt text](../images/eb.png)

![alt text](../images/aws_eb.png)
