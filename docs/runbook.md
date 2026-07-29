# Synthetic Data-Sharing Release Runbook

> Educational checklist only. It is not legal advice, a security procedure, or
> authorization to release real personal data.

## Before evaluation

1. Confirm the input is synthetic. Stop if it could contain real personal data.
2. Review the policy version, purpose, recipient, retention, and allowed fields.
3. Confirm every source field is classified as direct identifier, quasi-
   identifier, sensitive attribute, approved measure, or excluded.
4. Use only the demo key and fixed seed supplied for this repository.

## Gate review

### Transformation

- Original name, email, customer ID, postal code, age, and exact annual spend
  must not appear in the row-level output.
- Token columns must use distinct namespaces.
- Unexpected input columns must not be copied through.

### k-anonymity

- Review every equivalence class, not only the minimum.
- A failure blocks the candidate.
- A pass applies only to the declared quasi-identifiers; it is not proof against
  auxiliary-data linkage.
- Do not “fix” a failure by lowering `k` without a reviewed use-case decision.

### Noisy aggregate

- Confirm the privacy unit and contribution model—this demo does not implement
  either beyond one row per synthetic customer.
- Confirm bounds before noise.
- Confirm epsilon allocation and intended query count.
- Do not rerun with different seeds to select a preferred answer.
- Never publish this seeded educational output as a private statistic.

### Audit

- Recompute file and canonical policy hashes.
- Confirm row counts and all gate states.
- Treat the manifest as evidence, not as tamper-proof attestation.

## If a gate fails

1. Block the candidate artifact from leaving the evaluation environment.
2. Preserve the source hash, policy, reports, and failing equivalence classes.
3. Determine whether minimization, broader generalization, aggregation, or
   cancellation is appropriate.
4. Add a regression test for the failure.
5. Re-run the entire pipeline; do not manually edit the output.

## Incident indicators

- A direct identifier appears in shared output.
- A key or source dataset appears in logs or artifacts.
- A policy/hash mismatch occurs.
- A query is repeated beyond its approved budget.
- A recipient retains data beyond the approved period.

For any such event involving real data, stop this demo and follow the
organization’s actual privacy, legal, and security incident processes.
