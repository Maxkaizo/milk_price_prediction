FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9696

CMD ["gunicorn", "--bind", "0.0.0.0:9696", "app:app"]
