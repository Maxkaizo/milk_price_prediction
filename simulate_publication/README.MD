
# 🧪 Simulating Monthly Data Publication

This folder contains a script that simulates the **monthly publication of milk price data** in Mexico, as if released by a government agency (e.g., Secretaría de Economía).

In real-world MLOps pipelines, data is often ingested incrementally — one file per month, per source, or per region — from upstream systems or public portals. Since we only have a single historical Excel file, this simulation acts as the **starting point for our ML pipeline**.

---

## 🔍 Why simulate monthly publication?

Most real-world machine learning pipelines are built to:

- **Ingest new data monthly (or daily/weekly)**
- **Retrain or fine-tune models on recent data**
- **Validate performance using the most recent period**

To emulate this scenario, we take the single Excel file and **split it into monthly Parquet files**, stored in a structure similar to a Data Lake:

```bash

data/datalake/monthly/year=YYYY/month=MM/data.parquet

```

This allows us to later orchestrate training, validation, and model tracking as if new data were arriving month by month.

---

## ⚙️ How it works

Run the script:

```bash
python simulate_publication.py
```

It will:

1. Download the raw Excel file from the Secretaría de Economía.
2. Parse and transform it into a tabular format.
3. Partition the data into monthly `.parquet` files.
4. Save each file to the local `data/datalake/...` folder.
5. Optionally, upload each file to an S3 bucket (`mlops-milk-datalake`, private).

---

## 📁 Output example

``` bash
data
└── datalake
    └── monthly
        ├── 2024
        │   ├── 01
        │   │   └── 2024-01-data.parquet
        │   ├── 02
        │   │   └── 2024-02-data.parquet
        └── 2025
            ├── 01
            │   └── 2025-01-data.parquet
            ├── 02
            │   └── 2025-02-data.parquet
```

---

## 🌐 Source

Data provided by the Secretaría de Economía (Mexico) via:

> [https://www.economia-sniim.gob.mx](https://www.economia-sniim.gob.mx/Nuevo/home.aspx?Opcion=Default.aspx)

---

## 🧩 Next Step

This synthetic Data Lake will be used as the input for the Prefect-based training pipeline in the main MLOps workflow (`flows/train_pipeline.py`).

The pipeline will:

* Load data from specific months
* Train and validate an ML model
* Track performance with MLflow
* (Optionally) upload model artifacts to a remote registry

---



