from prefect import flow
from orchestration.tasks.prepare_full_dataset_s3 import prepare_full_dataset_s3


@flow(name="prepare-dataset-flow")
def run():
    output = prepare_full_dataset_s3(reference_date="2025-07-30")
    print(output)


if __name__ == "__main__":
    run()
