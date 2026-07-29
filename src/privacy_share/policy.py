"""Policy loading and validation for the educational sharing pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class PolicyError(ValueError):
    pass


@dataclass(frozen=True)
class SharingPolicy:
    name: str
    version: str
    dataset: str
    direct_identifiers: dict[str, str]
    quasi_identifiers: tuple[str, ...]
    minimum_k: int
    epsilon: float
    lower_bound: float
    upper_bound: float
    max_queries: int
    synthetic: bool
    raw: dict[str, Any]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SharingPolicy":
        required = (
            "name",
            "version",
            "dataset",
            "direct_identifiers",
            "quasi_identifiers",
            "k_anonymity",
            "differential_privacy",
        )
        missing = [name for name in required if name not in payload]
        if missing:
            raise PolicyError(f"Policy is missing: {', '.join(missing)}")
        direct = payload["direct_identifiers"]
        if not isinstance(direct, dict) or not direct:
            raise PolicyError("direct_identifiers must be a non-empty object")
        allowed_actions = {"tokenize", "drop"}
        invalid = {key: value for key, value in direct.items() if value not in allowed_actions}
        if invalid:
            raise PolicyError(f"Unsupported identifier actions: {invalid}")
        quasi = tuple(payload["quasi_identifiers"])
        if not quasi:
            raise PolicyError("quasi_identifiers cannot be empty")
        k = int(payload["k_anonymity"]["minimum_k"])
        if k < 2:
            raise PolicyError("minimum_k must be at least 2")
        dp = payload["differential_privacy"]
        epsilon = float(dp["epsilon"])
        lower = float(dp["lower_bound"])
        upper = float(dp["upper_bound"])
        max_queries = int(dp.get("max_queries", 1))
        if epsilon <= 0:
            raise PolicyError("epsilon must be positive")
        if lower >= upper:
            raise PolicyError("DP lower_bound must be less than upper_bound")
        if max_queries < 1:
            raise PolicyError("max_queries must be positive")
        return cls(
            name=str(payload["name"]),
            version=str(payload["version"]),
            dataset=str(payload["dataset"]),
            direct_identifiers={str(k): str(v) for k, v in direct.items()},
            quasi_identifiers=quasi,
            minimum_k=k,
            epsilon=epsilon,
            lower_bound=lower,
            upper_bound=upper,
            max_queries=max_queries,
            synthetic=bool(payload.get("synthetic", True)),
            raw=payload,
        )


def load_policy(path: str | Path) -> SharingPolicy:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PolicyError("Policy root must be an object")
    return SharingPolicy.from_dict(payload)
