PYTHON ?= python3
PYTHONPATH := src

.PHONY: help test check demo clean

help:
	@echo "test  - run offline tests"
	@echo "demo  - execute synthetic sharing policy and evidence flow"

test:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests -v

check:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m compileall -q src tests
	$(MAKE) test

demo:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m privacy_share demo \
		--input data/synthetic_customers.csv \
		--policy policies/research-share.policy.json \
		--output-dir .artifacts/demo \
		--demo-key not-a-production-secret \
		--seed 42 \
		--evaluated-at 2026-07-28T12:00:00Z

clean:
	rm -rf .artifacts
