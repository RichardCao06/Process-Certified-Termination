.PHONY: validate test

validate:
	python3 scripts/validate_p0.py
	python3 -m unittest discover -s tests -v

test: validate
