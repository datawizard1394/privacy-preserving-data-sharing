"""Audit-manifest construction with reproducible file provenance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .policy import SharingPolicy


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def policy_digest(policy: SharingPolicy) -> str:
    canonical = json.dumps(policy.raw, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def audit_manifest(
    *,
    policy: SharingPolicy,
    input_path: str | Path,
    output_path: str | Path,
    evaluated_at: str,
    source_rows: int,
    released_rows: int,
    k_report: dict[str, Any],
    dp_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "dataset": policy.dataset,
        "policy": {"name": policy.name, "version": policy.version},
        "policy_sha256": policy_digest(policy),
        "input_sha256": sha256_file(input_path),
        "output_sha256": sha256_file(output_path),
        "evaluated_at": evaluated_at,
        "row_counts": {"source": source_rows, "released": released_rows},
        "gates": {
            "k_anonymity": k_report["status"],
            "dp_query": {
                "status": "RECORDED",
                "query_id": dp_report["query_id"],
                "epsilon": dp_report["epsilon"],
                "mechanism": dp_report["mechanism"],
            },
        },
        "transformations": {
            "direct_identifiers": policy.direct_identifiers,
            "quasi_identifiers": list(policy.quasi_identifiers),
        },
        "educational_limitations_acknowledged": True,
        "synthetic_demo": True,
    }
