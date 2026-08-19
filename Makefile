.PHONY: test demo api

test:
	python -m unittest discover -s tests -v

demo:
	python scripts/generate_demo.py

api:
	uvicorn geochangelab.api:app --reload

