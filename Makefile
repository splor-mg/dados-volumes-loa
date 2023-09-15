.PHONY: all extract validate publish

EXT = txt
RESOURCE_NAMES := $(shell python main.py resources)
OUTPUT_FILES := $(addsuffix .csv,$(addprefix data/,$(RESOURCE_NAMES)))

all: extract validate

extract: 
	$(foreach resource_name, $(RESOURCE_NAMES),python main.py extract $(resource_name) &&) true

validate: 
	frictionless validate datapackage.yaml

publish: 
	git add -Af datapackage.json data/*.csv data-raw/*.$(EXT)
	git commit --author="Automated <actions@users.noreply.github.com>" -m "Update data package at: $$(date +%Y-%m-%dT%H:%M:%SZ)" || exit 0
	git push
