import unittest
from pathlib import Path

from privacy_share.io import read_csv
from privacy_share.policy import load_policy
from privacy_share.transform import pseudonymize, transform_records


ROOT = Path(__file__).resolve().parents[1]


class TransformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = read_csv(ROOT / "data/synthetic_customers.csv")
        cls.policy = load_policy(ROOT / "policies/research-share.policy.json")

    def test_pseudonym_is_stable_and_namespaced(self) -> None:
        first = pseudonymize("value", key=b"demo", namespace="customer")
        self.assertEqual(
            first, pseudonymize("value", key=b"demo", namespace="customer")
        )
        self.assertNotEqual(
            first, pseudonymize("value", key=b"demo", namespace="email")
        )

    def test_shared_rows_remove_direct_and_exact_sensitive_fields(self) -> None:
        shared = transform_records(self.source, self.policy, key=b"demo-key")
        row = shared[0]
        for field in (
            "customer_id",
            "full_name",
            "email",
            "postal_code",
            "age",
            "annual_spend_usd",
        ):
            self.assertNotIn(field, row)
        self.assertIn("customer_id_token", row)
        self.assertIn("email_token", row)
        self.assertEqual(row["age_band"], "20-29")
        self.assertEqual(row["spend_band"], "low")

    def test_empty_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            pseudonymize("value", key=b"", namespace="customer")


if __name__ == "__main__":
    unittest.main()
