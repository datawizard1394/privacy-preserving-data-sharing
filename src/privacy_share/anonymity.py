"""Equivalence-class diagnostics for k-anonymity."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


def k_anonymity_report(
    rows: list[dict[str, Any]],
    *,
    quasi_identifiers: Iterable[str],
    minimum_k: int,
) -> dict[str, Any]:
    quasi = tuple(quasi_identifiers)
    if minimum_k < 2:
        raise ValueError("minimum_k must be at least 2")
    if not quasi:
        raise ValueError("At least one quasi-identifier is required")
    groups = Counter(tuple(row.get(column) for column in quasi) for row in rows)
    violating = {key: size for key, size in groups.items() if size < minimum_k}
    affected = sum(violating.values())
    classes = [
        {
            "values": dict(zip(quasi, key)),
            "size": size,
            "passes": size >= minimum_k,
        }
        for key, size in sorted(groups.items(), key=lambda item: tuple(map(str, item[0])))
    ]
    return {
        "status": "PASS" if not violating else "FAIL",
        "minimum_k": minimum_k,
        "observed_minimum_class_size": min(groups.values()) if groups else 0,
        "quasi_identifiers": list(quasi),
        "equivalence_class_count": len(groups),
        "violating_class_count": len(violating),
        "affected_row_count": affected,
        "classes": classes,
        "limitations": [
            "k-anonymity does not prevent attribute disclosure within homogeneous groups.",
            "It does not model linkage using auxiliary data.",
            "Passing this diagnostic is not a security certification.",
        ],
        "synthetic_demo": True,
    }
