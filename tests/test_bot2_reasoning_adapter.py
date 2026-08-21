from bot2_reasoning_adapter import configured


def test_reasoning_is_fail_closed_without_provider(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    assert configured() is False


def test_reasoning_requires_all_provider_fields(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-only")
    monkeypatch.delenv("LLM_MODEL", raising=False)
    assert configured() is False
