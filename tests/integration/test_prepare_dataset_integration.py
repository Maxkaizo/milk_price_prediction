import hashlib
from pathlib import Path
from orchestration.tasks.prepare_full_dataset_s3 import prepare_full_dataset_s3


def compute_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def test_dataset_generation_hash(tmp_path):
    # Ejecuta la tarea con una fecha fija
    output_path = prepare_full_dataset_s3(reference_date="2025-08-01")

    # Compara contra hash conocido
    generated_hash = compute_sha256(Path(output_path))
    expected_hash = "966b1331182543d398697806702497c9918896a9de9ccfb6ced5864573b3e2de"

    assert (
        generated_hash == expected_hash
    ), "Generated dataset does not match known hash"
