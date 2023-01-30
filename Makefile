DOCKER_IMAGE?=sbert-service
LICENSE=LICENSE
LICENSE_HEADER=LICENSE_HEADER
VENV=.venv
$(VENV):
	$(MAKE) install

.PHONY: install
install: poetry-ensure-installed
	poetry config --local virtualenvs.in-project true
	poetry env use python3.10
	poetry install

.PHONY docker-build:
docker-build: sentence-transformers transformer.pkl
# squash reduces final image size by merging layers `--squash`
# but its not supported in github actions
	docker build -t $(DOCKER_IMAGE) .

shared/installed:
	mkdir -p shared/installed

sentence-transformers: shared/installed
#	cd shared && python sentence_transformer_download.py
	cd shared && ./transformer_download.sh

transformer.pkl: $(VENV) shared/installed sentence-transformers
	poetry run python ./server/transformer/embeddings.py ./shared/installed

build/deploy:
	# put everything we want in our beanstalk deploy.zip file
	# into a build/deploy folder.
	mkdir -p build/deploy
	cp -r ebs/bundle build/deploy/bundle

deploy.zip:
	$(MAKE) clean-deploy build/deploy
	cd build/deploy/bundle && zip -r $(PWD)/deploy.zip .

clean-deploy:
	rm -rf build deploy.zip

.PHONY clean:
clean:
	rm -rf .venv htmlcov .coverage build deploy.zip

.PHONY: deps-show
deps-show:
	poetry show

.PHONY: deps-show
deps-show-outdated:
	poetry show --outdated

.PHONY: deps-update
deps-update:
	poetry update

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
	./tools/poetry_ensure_installed.sh

.PHONY: test
test: $(VENV)
	cd ./shared/ && $(MAKE) installed/sentence-transformer
	SHARED_ROOT=./shared/installed poetry run python -m pytest -vv

.PHONY: black
black: $(VENV)
	poetry run black .

.PHONY: format
format:
	$(MAKE) license
	$(MAKE) black

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
