.PHONY: validate validate-p0 validate-p1 validate-calibration validate-development-pilot validate-analysis-readiness validate-closure-readiness validate-closure validate-p2-foundation validate-p2-active validate-p2-natural-pilot-preflight validate-p2-dsh-conformance validate-p2-d19 validate-p2-engineering-smoke validate-p2-d20 synthetic-p2-regression unit test materialize-calibration materialize-p1-closure

validate: validate-p0 validate-p1 validate-calibration validate-development-pilot validate-analysis-readiness validate-closure-readiness validate-closure validate-p2-foundation validate-p2-active validate-p2-natural-pilot-preflight validate-p2-dsh-conformance validate-p2-d19 validate-p2-engineering-smoke validate-p2-d20 unit

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

validate-p2-active:
	python3 scripts/validate_p2_active.py

validate-p2-natural-pilot-preflight:
	python3 scripts/validate_p2_natural_pilot_preflight.py

validate-p2-dsh-conformance:
	python3 scripts/validate_p2_dsh_conformance.py

validate-p2-d19:
	python3 scripts/validate_p2_d19.py

validate-p2-engineering-smoke:
	python3 scripts/validate_p2_engineering_smoke.py

validate-p2-d20:
	python3 scripts/validate_p2_d20.py

synthetic-p2-regression:
	python3 scripts/run_p2_synthetic_regression.py

unit:
	python3 -m unittest discover -s tests -v

materialize-calibration:
	python3 scripts/materialize_p1_calibration.py

materialize-p1-closure:
	python3 scripts/materialize_p1_closure_readiness.py

test: validate
