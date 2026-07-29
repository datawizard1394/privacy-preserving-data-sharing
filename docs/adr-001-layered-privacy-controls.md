# ADR-001: Layer minimization, pseudonymization, anonymity diagnostics, and aggregates

- **Status:** Accepted for this educational demo
- **Date:** 2026-07-28
- **Scope:** Synthetic data only

## Context

No single transformation makes arbitrary row-level data “safe.” Dropping names
does not address quasi-identifiers; stable tokens permit linkage; k-anonymity
has known disclosure limitations; differential privacy requires careful
accounting and release controls.

## Decision

Model sharing as a policy-gated sequence:

1. minimize direct identifiers;
2. tokenize only approved linkage fields using a namespaced keyed function;
3. generalize selected quasi-identifiers;
4. block the row-level candidate if an equivalence class is below `k`;
5. calculate a separate bounded noisy aggregate for educational inspection;
6. emit a provenance manifest containing policy and artifact hashes.

Exact spend is never written to the row-level shared candidate. The noisy
aggregate reads it from the source path.

## Why this is not a security claim

- The demo key is supplied at the command line and has no lifecycle controls.
- Stable pseudonyms deliberately support linkage.
- k-anonymity does not bound membership inference or attribute disclosure.
- The seeded PRNG is deterministic, not appropriate for a real private release.
- There is no budget accountant or privacy-unit contribution model.
- File hashes are not signatures or an immutable audit service.

## Consequences

### Positive

- Policy intent is reviewable and versioned.
- Direct identifiers cannot accidentally survive an allow-by-default copy.
- Equivalence classes are inspectable rather than summarized as a single badge.
- The aggregate reports bounds and epsilon allocation.
- Tests can reproduce and challenge every stage.

### Trade-offs

- Generalization reduces utility.
- Linkable tokens remain sensitive.
- A pass is conditional on the declared quasi-identifiers and available data.
- The demonstration cannot be promoted to production by changing configuration.

## Alternatives rejected

1. **Hash identifiers without a key:** vulnerable to straightforward dictionary
   matching for low-entropy values.
2. **Call tokenization “anonymous”:** misleading because stable records remain
   linkable.
3. **Publish an exact aggregate beside a noisy one:** defeats the educational
   release boundary.
4. **Claim formal DP from a compact sample:** rejected without secure randomness,
   accounting, contribution bounding, and expert review.
