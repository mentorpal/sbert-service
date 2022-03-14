LICENSE=LICENSE
LICENSE_HEADER=LICENSE_HEADER
VENV=.venv
$(VENV):
	$(MAKE) install

.PHONY: install
install: poetry-ensure-installed
	poetry config --local virtualenvs.in-project true
	poetry env use python3.8
	poetry install

.PHONY: deps-show
deps-show:
	poetry show

.PHONY: deps-show
deps-show-outdated:
	poetry show --outdated

.PHONY: deps-update
deps-update:
	poetry update

.PHONY clean:
clean:
	rm -rf .venv htmlcov .coverage

.PHONY: docker-build
docker-build:
	cd server && $(MAKE) docker-build

.PHONY: black
black: $(VENV)
	poetry run black .

.PHONY: format
format:
	$(MAKE) license
	$(MAKE) black

LICENSE:
	@echo "you must have a LICENSE file" 1>&2
	exit 1

LICENSE_HEADER:
	@echo "you must have a LICENSE_HEADER file" 1>&2
	exit 1

.PHONY: license
license: LICENSE LICENSE_HEADER $(VENV)
	poetry run python -m licenseheaders -t LICENSE_HEADER -d server $(args)
	poetry run python -m licenseheaders -t LICENSE_HEADER -d tests $(args)
	poetry run python -m licenseheaders -t LICENSE_HEADER -d tools $(args)

.PHONY: poetry-ensure-installed
poetry-ensure-installed:
	sh ./tools/poetry_ensure_installed.sh

.PHONY: test
test: $(VENV)
	cd ./shared/ && $(MAKE) installed/sentence-transformer
	SHARED_ROOT=./shared/installed poetry run coverage run \
		--omit="$(PWD)/tests $(VENV)" \
		-m py.test -vv $(args)


.PHONY: test-all
test-all:
	$(MAKE) test-license
	$(MAKE) test-format
	$(MAKE) test-lint
	$(MAKE) test-types
	$(MAKE) test

.PHONY: test-format
test-format: $(VENV)
	poetry run black --check .

.PHONY: test-lint
test-lint: $(VENV)
	poetry run flake8 .

.PHONY: test-license
test-license: LICENSE LICENSE_HEADER
	args="--check" $(MAKE) license

.PHONY: test-types
test-types: $(VENV)
	poetry run mypy server
