from pathlib import Path
from worker_runtime_guard import validate_allocation, sha256_file


def test_missing_execution_tuple_is_blocked():
    ok, errors = validate_allocation({"allocation_id":"A","cycle_id":"C","worker_id":"BOT2_QUANT_WORKER"}, "BOT2_QUANT_WORKER")
    assert not ok
    assert "missing_task_id" in errors
    assert "missing_input_artifact" in errors
    assert "missing_model_version" in errors


def test_hash_mismatch_is_blocked(tmp_path: Path):
    p = tmp_path / "input.bin"
    p.write_bytes(b"actual")
    allocation = {
        "allocation_id":"A","cycle_id":"C","task_id":"T","task_type":"QUANT",
        "worker_id":"BOT2_QUANT_WORKER","input_artifact":str(p),"input_sha256":"0"*64,
        "model_version":"v1"
    }
    ok, errors = validate_allocation(allocation, "BOT2_QUANT_WORKER")
    assert not ok
    assert "input_sha256_mismatch" in errors
    assert sha256_file(p) != "0"*64
