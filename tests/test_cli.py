import csv
import json
import tempfile
import unittest
from pathlib import Path

from privacy_share.cli import main


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_demo_writes_policy_and_audit_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            result = main(
                [
                    "demo",
                    "--input",
                    str(ROOT / "data/synthetic_customers.csv"),
                    "--policy",
                    str(ROOT / "policies/research-share.policy.json"),
                    "--output-dir",
                    str(output),
                    "--demo-key",
                    "not-a-production-secret",
                    "--seed",
                    "42",
                    "--evaluated-at",
                    "2026-07-28T12:00:00Z",
                ]
            )
            self.assertEqual(result, 0)
            summary = json.loads(
                (output / "summary.json").read_text(encoding="utf-8")
            )
            audit = json.loads(
                (output / "audit-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(summary["status"], "PASS")
            self.assertTrue(audit["educational_limitations_acknowledged"])
            with (output / "shared-dataset.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                header = next(csv.reader(handle))
            self.assertNotIn("full_name", header)
            self.assertNotIn("annual_spend_usd", header)
            self.assertTrue((output / "k-anonymity-report.json").exists())
            self.assertTrue((output / "dp-aggregate.json").exists())


if __name__ == "__main__":
    unittest.main()
