.PHONY: venv deps run

venv:
	python3 -m venv .venv

deps:
	. .venv/bin/activate && pip install -r requirements.txt

run:
	. .venv/bin/activate && python -m engine.flow_controller
