"""Policy-driven pseudonymization and generalization transformations."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

from .policy import SharingPolicy


def pseudonymize(value: str, *, key: bytes, namespace: str) -> str:
    """Return a stable educational pseudonym using keyed HMAC.

    HMAC is used as a standard primitive, but this function alone does not
    provide production tokenization: there is no vault, rotation, access
    control, revocation, or protection against linkage and auxiliary data.
    """

    if not key:
        raise ValueError("Pseudonymization key cannot be empty")
    message = f"{namespace}\x00{value}".encode("utf-8")
    digest = hmac.new(key, message, hashlib.sha256).hexdigest()
    return f"tok_{digest[:24]}"


def age_band(value: str) -> str:
    age = int(value)
    if not 0 <= age <= 120:
        raise ValueError(f"Age outside supported range: {age}")
    lower = age // 10 * 10
    return f"{lower:02d}-{lower + 9:02d}"


def spend_band(value: str) -> str:
    amount = float(value)
    if amount < 0:
        raise ValueError("annual_spend_usd cannot be negative")
    if amount < 1000:
        return "low"
    if amount < 5000:
        return "medium"
    return "high"


def transform_records(
    rows: list[dict[str, str]],
    policy: SharingPolicy,
    *,
    key: bytes,
) -> list[dict[str, Any]]:
    shared: list[dict[str, Any]] = []
    for row in rows:
        transformed: dict[str, Any] = {}
        for column, action in policy.direct_identifiers.items():
            if column not in row:
                raise ValueError(f"Missing direct identifier: {column}")
            if action == "tokenize":
                transformed[f"{column}_token"] = pseudonymize(
                    row[column], key=key, namespace=f"{policy.name}:{column}"
                )
        transformed.update(
            {
                "age_band": age_band(row["age"]),
                "region": row["region"],
                "spend_band": spend_band(row["annual_spend_usd"]),
                "support_tier": row["support_tier"],
                "synthetic_demo": True,
            }
        )
        shared.append(transformed)
    return shared
