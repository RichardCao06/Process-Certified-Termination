.PHONY: validate validate-p0 validate-p1 validate-calibration validate-development-pilot unit test materialize-calibration

validate: validate-p0 validate-p1 validate-calibration validate-development-pilot unit

validate-p0:
	python3 scripts/validate_p0.py

validate-p1:
	python3 scripts/validate_p1.py

validate-calibration:
	python3 scripts/validate_p1_calibration_current.py

validate-development-pilot:
	python3 scripts/validate_p1_development_pilot.py

unit:
	python3 -m unittest discover -s tests -v

materialize-calibration:
	python3 scripts/materialize_p1_calibration.py

test: validate
