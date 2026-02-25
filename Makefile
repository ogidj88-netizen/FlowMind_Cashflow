# FlowMind_Cashflow — Makefile (Selftest Utilities)

PROJECT ?= FM_TEST_001

.PHONY: help selftest-delivery clean-test compile

help:
	@echo "Targets:"
	@echo "  make compile                 - python syntax check (key modules)"
	@echo "  make selftest-delivery       - generate dummy final + run delivery QA"
	@echo "  make clean-test              - remove out/<PROJECT>/ artifacts"
	@echo ""
	@echo "Vars:"
	@echo "  PROJECT=FM_TEST_001 (default)  e.g.: make selftest-delivery PROJECT=FM_TEST_002"

compile:
	python3 -m py_compile engine/artifacts.py
	python3 -m py_compile engine/delivery/__init__.py
	python3 -m py_compile engine/delivery/router.py
	python3 -m py_compile engine/delivery/run_delivery_cli.py
	python3 -m py_compile engine/delivery/qa/qa_finalize_v1.py

selftest-delivery: compile
	bash engine/assembly/make_dummy_final_v2.sh $(PROJECT)
	python3 -m engine.delivery.run_delivery_cli $(PROJECT)

clean-test:
	rm -rf out/$(PROJECT)
	@echo "[OK] removed out/$(PROJECT)"
