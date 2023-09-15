.PHONY: all extract validate publish

RESOURCE_NAMES := $(shell python main.py resources)
DATA_FILES := $(shell python main.py resources --path)

all: extract validate

extract: 
	$(foreach resource_name, $(RESOURCE_NAMES),python main.py extract $(resource_name) &&) true

validate: 
	frictionless validate datapackage.yaml

build: datapackage.json

datapackage.json: $(DATA_FILES) scripts/build.py datapackage.yaml
	python main.py build

check:
	frictionless validate datapackage.json

publish: 
	git add -Af datapackage.json data-raw/*.xlsx
	git commit --author="Automated <actions@users.noreply.github.com>" -m "Update data package at: $$(date +%Y-%m-%dT%H:%M:%SZ)" || exit 0
	git push
