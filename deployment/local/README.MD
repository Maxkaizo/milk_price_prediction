# Roadmap:

* Entirely Local. Local files + Flask
* Entirely Local + gunicorn
* Local with Docker container + gunicorn
* Cloud deployment using Elastic Beanstalk (with Docker image)


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
