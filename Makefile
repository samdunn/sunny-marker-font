PYTHON ?= python3

.PHONY: build package verify proof preview
build:
	$(PYTHON) scripts/build.py

package:
	$(PYTHON) scripts/package_gf.py

verify:
	$(PYTHON) scripts/verify_fonts.py

proof:
	$(PYTHON) -c "import sys; sys.path.insert(0, 'scripts'); import verify_fonts; verify_fonts.proof()"

preview:
	$(PYTHON) -m http.server 8766 --bind 127.0.0.1 --directory web

.PHONY: check
check:
	$(PYTHON) scripts/check_fontbakery.py

.PHONY: sources audit atlas submission review
sources:
	$(PYTHON) scripts/make_weights.py
	$(PYTHON) scripts/make_variable.py
	$(PYTHON) scripts/regularize_sources.py
	$(PYTHON) scripts/simplify_sources.py
	$(PYTHON) scripts/fit_sources.py
	$(PYTHON) scripts/round_source_joins.py
	$(PYTHON) scripts/prepare_layout.py
	$(PYTHON) scripts/polish_sources.py

audit:
	$(PYTHON) -m pip check
	$(PYTHON) -m pip_audit
	$(PYTHON) -m bandit -r scripts -ll

atlas:
	$(PYTHON) scripts/glyph_atlas.py

submission:
	$(PYTHON) scripts/package_submission.py

review:
	$(PYTHON) scripts/build_review.py

.PHONY: coverage-review coverage-verify
coverage-review:
	$(PYTHON) scripts/build_coverage_candidate.py

coverage-verify:
	$(PYTHON) scripts/verify_coverage_candidate.py

.PHONY: npm
npm:
	$(PYTHON) scripts/package_npm.py

.PHONY: outline-sources outline-review outline-verify
# Rebuild candidates/1.315/sources.zip from the archived 1.314 sources.
outline-sources:
	$(PYTHON) scripts/make_outline_sources.py

outline-review:
	$(PYTHON) scripts/build_coverage_candidate.py --version 1.315

outline-verify:
	$(PYTHON) scripts/verify_outline_candidate.py
