SHELL := /usr/bin/env bash
APP_PORT ?= 5173
APP_PID := .app.pid

.PHONY: install serve serve-stop test test-headed test-debug report serve-report lint clean

install:
	python -m pip install -e ".[dev]"
	playwright install --with-deps chromium

serve:
	@python -m http.server $(APP_PORT) --bind 127.0.0.1 -d ../app & echo $$! > $(APP_PID); \
	  echo "TaskFlow on http://127.0.0.1:$(APP_PORT) (pid $$(cat $(APP_PID)))"

serve-stop:
	@if [ -f $(APP_PID) ]; then \
	  kill $$(cat $(APP_PID)) 2>/dev/null || true; \
	  rm -f $(APP_PID); \
	  echo "TaskFlow stopped"; \
	fi

test:
	@$(MAKE) serve
	@for i in $$(seq 1 20); do \
	  curl -s -o /dev/null http://127.0.0.1:$(APP_PORT)/ && break; \
	  sleep 0.2; \
	done
	@vedro run -vv; status=$$?; $(MAKE) serve-stop; exit $$status

test-headed:
	@$(MAKE) serve
	@vedro run -vv -- --pw-headed --pw-slowmo 250; status=$$?; $(MAKE) serve-stop; exit $$status

test-debug:
	@$(MAKE) serve
	@vedro run -vv -- --pw-headed --pw-debug; status=$$?; $(MAKE) serve-stop; exit $$status

report:
	allure generate allure-results --clean -o allure-report

serve-report:
	allure serve allure-results

lint:
	ruff check .

clean:
	rm -rf allure-results allure-report .pytest_cache .mypy_cache .ruff_cache $(APP_PID)
	find . -type d -name "__pycache__" -exec rm -rf {} +
