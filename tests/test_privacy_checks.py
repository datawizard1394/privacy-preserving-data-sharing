import copy
import unittest
from pathlib import Path

from privacy_share.anonymity import k_anonymity_report
from privacy_share.differential import dp_mean
from privacy_share.io import read_csv
from privacy_share.policy import load_policy
from privacy_share.transform import transform_records


ROOT = Path(__file__).resolve().parents[1]


class PrivacyCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = read_csv(ROOT / "data/synthetic_customers.csv")
        cls.policy = load_policy(ROOT / "policies/research-share.policy.json")
        cls.shared = transform_records(source, cls.policy, key=b"demo-key")

    def test_fixture_satisfies_policy_k(self) -> None:
        report = k_anonymity_report(
            self.shared,
            quasi_identifiers=self.policy.quasi_identifiers,
            minimum_k=self.policy.minimum_k,
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["observed_minimum_class_size"], 2)
        self.assertEqual(report["equivalence_class_count"], 4)

    def test_unique_group_fails_k_gate(self) -> None:
        rows = copy.deepcopy(self.shared)
        rows[0]["region"] = "UNIQUE"
        report = k_anonymity_report(
            rows,
            quasi_identifiers=self.policy.quasi_identifiers,
            minimum_k=2,
        )
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["affected_row_count"], 2)

    def test_dp_example_is_reproducible_and_bounded(self) -> None:
        kwargs = {
            "epsilon": 1.0,
            "lower_bound": 0,
            "upper_bound": 10000,
            "seed": 42,
            "query_id": "mean-v1",
        }
        first = dp_mean([500, 700, 2000, 3000], **kwargs)
        second = dp_mean([500, 700, 2000, 3000], **kwargs)
        self.assertEqual(first, second)
        self.assertGreaterEqual(first["noisy_mean"], 0)
        self.assertLessEqual(first["noisy_mean"], 10000)
        self.assertIn("not secure release", first["limitations"][0])


if __name__ == "__main__":
    unittest.main()
