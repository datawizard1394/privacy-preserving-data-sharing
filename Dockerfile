FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src
WORKDIR /app
RUN useradd --create-home --uid 10001 privacydemo
COPY --chown=privacydemo:privacydemo src ./src
COPY --chown=privacydemo:privacydemo data ./data
COPY --chown=privacydemo:privacydemo policies ./policies
USER privacydemo
ENTRYPOINT ["python", "-m", "privacy_share"]
CMD ["demo", "--input", "data/synthetic_customers.csv", "--policy", "policies/research-share.policy.json", "--output-dir", "/tmp/privacy-demo", "--demo-key", "not-a-production-secret", "--seed", "42", "--evaluated-at", "2026-07-28T12:00:00Z"]
