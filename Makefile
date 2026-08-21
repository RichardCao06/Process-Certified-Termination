.PHONY: validate validate-p0 validate-p1 unit test

validate: validate-p0 validate-p1 unit

validate-p0:
	python3 scripts/validate_p0.py

validate-p1:
	python3 scripts/validate_p1.py

unit:
	python3 -m unittest discover -s tests -v

test: validate
