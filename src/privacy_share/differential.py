"""Educational Laplace-mechanism aggregate with explicit limitations."""

from __future__ import annotations

import math
import random
from typing import Iterable


def _laplace(rng: random.Random, scale: float) -> float:
    uniform = rng.random() - 0.5
    return -scale * math.copysign(math.log1p(-2 * abs(uniform)), uniform)


def dp_mean(
    values: Iterable[float],
    *,
    epsilon: float,
    lower_bound: float,
    upper_bound: float,
    seed: int,
    query_id: str,
) -> dict:
    """Return a reproducible educational noisy mean.

    The epsilon budget is split equally between a bounded sum and a count. A
    seeded non-secure PRNG makes tests reproducible; this alone is not a
    production differential-privacy implementation or privacy accountant.
    """

    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    if lower_bound >= upper_bound:
        raise ValueError("lower_bound must be less than upper_bound")
    bounded = [min(max(float(value), lower_bound), upper_bound) for value in values]
    if not bounded:
        raise ValueError("At least one value is required")
    half_epsilon = epsilon / 2
    rng = random.Random(f"{seed}:{query_id}")
    sum_sensitivity = upper_bound - lower_bound
    noisy_sum = sum(bounded) + _laplace(rng, sum_sensitivity / half_epsilon)
    noisy_count = len(bounded) + _laplace(rng, 1 / half_epsilon)
    safe_count = max(1.0, noisy_count)
    noisy_mean = min(max(noisy_sum / safe_count, lower_bound), upper_bound)
    return {
        "mechanism": "educational_laplace_mean",
        "query_id": query_id,
        "epsilon": epsilon,
        "epsilon_allocation": {"bounded_sum": half_epsilon, "count": half_epsilon},
        "bounds": {"lower": lower_bound, "upper": upper_bound},
        "noisy_mean": round(noisy_mean, 2),
        "noisy_count": round(noisy_count, 2),
        "clamped_input_count": len(bounded),
        "limitations": [
            "A deterministic seeded PRNG is used for reproducible education, not secure release.",
            "No composition accountant, contribution bounding across users, or query ledger is implemented.",
            "Do not publish repeated seeded outputs or treat this as production differential privacy.",
        ],
        "synthetic_demo": True,
    }
