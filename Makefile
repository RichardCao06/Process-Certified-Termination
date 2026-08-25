.PHONY: validate validate-p0 validate-p1 validate-calibration validate-development-pilot validate-analysis-readiness validate-closure-readiness validate-closure validate-p2-foundation unit test materialize-calibration materialize-p1-closure

validate: validate-p0 validate-p1 validate-calibration validate-development-pilot validate-analysis-readiness validate-closure-readiness validate-closure validate-p2-foundation unit

validate-p0:
	python3 scripts/validate_p0.py

validate-p1:
	python3 scripts/validate_p1.py

validate-calibration:
	python3 scripts/validate_p1_calibration_current.py

validate-development-pilot:
	python3 scripts/validate_p1_development_pilot.py

validate-analysis-readiness:
	python3 scripts/validate_p1_analysis_readiness.py

validate-closure-readiness:
	python3 scripts/validate_p1_closure_readiness.py

validate-closure:
	python3 scripts/validate_p1_closure.py

validate-p2-foundation:
	python3 scripts/validate_p2_foundation.py

unit:
	python3 -m unittest discover -s tests -v

materialize-calibration:
	python3 scripts/materialize_p1_calibration.py

materialize-p1-closure:
	python3 scripts/materialize_p1_closure_readiness.py

test: validate
