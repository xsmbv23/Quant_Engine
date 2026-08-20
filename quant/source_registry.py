"""Authoritative source admission metadata for Layer 1.

This module does not fetch data and does not declare truth. It only validates
whether a requested source is registered and whether an adapter is declared.
Brain remains the governance authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "source_registry_v1.json"


@dataclass(frozen=True)
class SourceAdmission:
    source_id: str
    domain: str
    role: str
    adapter_required: bool
    network_origin_proof_required: bool
    official_result_panel_required: bool
    status: str


def _load() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def registered_sources() -> tuple[SourceAdmission, ...]:
    data = _load()
    return tuple(SourceAdmission(**{k: item[k] for k in (
        "source_id", "domain", "role", "adapter_required",
        "network_origin_proof_required", "official_result_panel_required", "status"
    )}) for item in data["registered_sources"])


def admit_source(source_id: str, *, adapter_available: bool) -> SourceAdmission:
    for source in registered_sources():
        if source.source_id == source_id:
            if source.adapter_required and not adapter_available:
                raise PermissionError("SOURCE_REGISTERED_WITHOUT_ADAPTER_DENY")
            return source
    raise PermissionError("SOURCE_UNREGISTERED_DENY")
