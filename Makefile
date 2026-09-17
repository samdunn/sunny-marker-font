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

.PHONY: sources audit atlas submission
sources:
	$(PYTHON) scripts/make_weights.py
	$(PYTHON) scripts/make_variable.py
	$(PYTHON) scripts/simplify_sources.py
	$(PYTHON) scripts/fit_sources.py

audit:
	$(PYTHON) -m pip check
	$(PYTHON) -m pip_audit
	$(PYTHON) -m bandit -r scripts -ll

atlas:
	$(PYTHON) scripts/glyph_atlas.py

submission:
	$(PYTHON) scripts/package_submission.py

.PHONY: npm
npm:
	$(PYTHON) scripts/package_npm.py
