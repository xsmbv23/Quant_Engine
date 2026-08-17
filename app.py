import json
import sys
from pathlib import Path

from input_adapter import get_last_n_days
from room_01_signal import generate_candidates
from scoring import score_candidates


def run_pipeline(data):
    window = get_last_n_days(data, 30)
    candidates = generate_candidates(window)
    ranked = score_candidates(candidates)
    return {
        "window_days": len(window),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "ranked": ranked,
    }


def load_input(path: str):
    """Load canonical JSON exported by the upstream data plane.

    No synthetic fallback is provided. Missing/invalid input is an execution
    error rather than an invitation to manufacture data.
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python app.py <canonical-data.json>")
    result = run_pipeline(load_input(sys.argv[1]))
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
