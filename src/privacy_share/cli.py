"""CLI for the synthetic policy-driven data-sharing demonstration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .anonymity import k_anonymity_report
from .audit import audit_manifest
from .differential import dp_mean
from .io import read_csv, write_csv, write_json
from .policy import PolicyError, load_policy
from .transform import transform_records


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="privacy-share")
    command = root.add_subparsers(dest="command", required=True)
    demo = command.add_parser("demo", help="execute the educational sharing flow")
    demo.add_argument("--input", type=Path, required=True)
    demo.add_argument("--policy", type=Path, required=True)
    demo.add_argument("--output-dir", type=Path, default=Path(".artifacts/demo"))
    demo.add_argument("--demo-key", required=True)
    demo.add_argument("--seed", type=int, default=42)
    demo.add_argument("--evaluated-at", required=True)
    return root


def run_demo(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    source = read_csv(args.input)
    shared = transform_records(source, policy, key=args.demo_key.encode("utf-8"))
    k_report = k_anonymity_report(
        shared,
        quasi_identifiers=policy.quasi_identifiers,
        minimum_k=policy.minimum_k,
    )
    dp_report = dp_mean(
        (float(row["annual_spend_usd"]) for row in source),
        epsilon=policy.epsilon,
        lower_bound=policy.lower_bound,
        upper_bound=policy.upper_bound,
        seed=args.seed,
        query_id="annual-spend-mean-v1",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    shared_path = args.output_dir / "shared-dataset.csv"
    write_csv(shared_path, shared)
    write_json(args.output_dir / "k-anonymity-report.json", k_report)
    write_json(args.output_dir / "dp-aggregate.json", dp_report)
    manifest = audit_manifest(
        policy=policy,
        input_path=args.input,
        output_path=shared_path,
        evaluated_at=args.evaluated_at,
        source_rows=len(source),
        released_rows=len(shared),
        k_report=k_report,
        dp_report=dp_report,
    )
    write_json(args.output_dir / "audit-manifest.json", manifest)
    summary = {
        "status": "PASS" if k_report["status"] == "PASS" else "BLOCKED",
        "released_rows": len(shared) if k_report["status"] == "PASS" else 0,
        "k_anonymity": k_report["status"],
        "dp_query": "EDUCATIONAL_ONLY",
        "synthetic_demo": True,
    }
    write_json(args.output_dir / "summary.json", summary)
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 1


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return run_demo(args)
    except (OSError, ValueError, KeyError, PolicyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
