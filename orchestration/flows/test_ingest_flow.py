from prefect import flow
from orchestration.tasks.check_file_availability import check_file_availability
from orchestration.tasks.extract_and_ingest_today import extract_and_ingest_today

@flow(name="check-and-download-daily-leche")
def main():
    should_run = check_file_availability()
    if should_run:
        s3_path = extract_and_ingest_today()
        print(f"✅ File ingested and uploaded to: {s3_path}")
    else:
        print("🚫 No new file to process today.")

if __name__ == "__main__":
    main()
