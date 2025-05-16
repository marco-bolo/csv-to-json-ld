
.PHONY: dockersetup output-directories jsonld clean bulk-ttl bulk-jsonld all init remove-orphaned shacl-report

WORKING_DIR			:= $(shell pwd)
UID					:= $(shell id -u)
GID					:= $(shell id -g)

CSVW_CHECK_DOCKER	:= roblinksdata/csvw-check:latest
CSV2RDF_DOCKER		:= europe-west2-docker.pkg.dev/swirrl-devops-infrastructure-1/public/csv2rdf:v0.7.1
JENA_CLI_DOCKER		:= gsscogs/gss-jvm-build-tools:latest
MBO_TOOLS_DOCKER	:= ghcr.io/marco-bolo/csv-to-json-ld-tools:latest

CSVW_CHECK						:= docker run --rm -v "$(WORKING_DIR)":/work -u $(UID):$(GID) -w /work $(CSVW_CHECK_DOCKER) -s
CSV2RDF							:= docker run --rm -v "$(WORKING_DIR)":/work -u $(UID):$(GID) -w /work $(CSV2RDF_DOCKER) csv2rdf -m minimal -u 
RIOT							:= docker run --rm -v "$(WORKING_DIR)":/work -u $(UID):$(GID) -w /work $(JENA_CLI_DOCKER) riot
SPARQL							:= docker run --rm -v "$(WORKING_DIR)":/work -u $(UID):$(GID) -w /work $(JENA_CLI_DOCKER) sparql

MBO_TOOLS_DOCKER_RUN			:= docker run -i --rm -v "$(WORKING_DIR)":/work -u $(UID):$(GID) -w /work "$(MBO_TOOLS_DOCKER)"
CONVERT_LIST_VALUES_TO_NODES	:= $(MBO_TOOLS_DOCKER_RUN) listcolumnsasnodes
LIST_COLUMN_FOREIGN_KEY_CHECK	:= $(MBO_TOOLS_DOCKER_RUN) listcolumnforeignkeycheck
UNION_UNIQUE_IDENTIFIERS		:= $(MBO_TOOLS_DOCKER_RUN) unionuniqueidentifiers
JQ								:= $(MBO_TOOLS_DOCKER_RUN) jq
JSONLD_CLI						:= $(MBO_TOOLS_DOCKER_RUN) jsonld
SHACL_CLI						:= $(MBO_TOOLS_DOCKER_RUN) pyshacl 

CSVW_METADATA_FILES 			:= $(wildcard remote/*.csv-metadata.json)
CSVW_METADATA_VALIDATION_FILES	:= $(CSVW_METADATA_FILES:remote/%.csv-metadata.json=out/validation/%.success.log)
BULK_TTL_FILES    				:= $(CSVW_METADATA_FILES:remote/%.csv-metadata.json=out/bulk/%.ttl)
EXPECTED_BULK_OUT_FILES			:= $(BULK_TTL_FILES)

include remote/foreign-keys.mk

dockersetup:
	@echo "=============================== Pulling & Building required docker images. ==============================="
	@docker pull $(CSVW_CHECK_DOCKER)
	@docker pull $(CSV2RDF_DOCKER)
	@docker pull $(JENA_CLI_DOCKER)
	@docker pull $(MBO_TOOLS_DOCKER)
	@echo "" ; 

out/validation/person-or-organization.csv: Person.csv Organization.csv 
	@mkdir -p out/validation
	@$(UNION_UNIQUE_IDENTIFIERS) --out out/validation/person-or-organization.csv --column-name "MBO Permanent Identifier*" Person.csv Organization.csv

validate: $(CSVW_METADATA_VALIDATION_FILES) $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS)
	@EXIT_CODE=0; \
	 for file in $$(find out/validation/*.err.log); \
	 do \
	 	EXIT_CODE=1; \
		printf '[0;31m'; # Red \
		echo "Errors detected:"; \
		echo ""; \
		cat "$$file"; \
	   	printf '[0m'; # Reset colour \
	 done; \
	 exit "$$EXIT_CODE";

out/bulk/%.json: out/bulk/%.ttl
	@echo "=============================== Converting $< to JSON-LD $@ ===============================" ;
	@$(RIOT) --syntax ttl --out json-ld "$<" > "$@";
	@echo "";

out/bulk/All.trig: $(BULK_TTL_FILES)
	@$(SPARQL) --quiet $(^:out/bulk/%.ttl=--namedGraph out/bulk/%.ttl) "CONSTRUCT { GRAPH ?g { ?s ?p ?o. } } WHERE { GRAPH ?g { ?s ?p ?o. } }" > out/bulk/All.trig

shacl-report: out/bulk/All.trig
	@echo "The SHACL Report:"
	@echo ""
	@echo "First looking for any violations:"
	@echo ""
	
	@# This will cause the build process to fail if there are any violations.
	@$(SHACL_CLI) --format table --shapes remote/shacl.ttl --allow-info --allow-warning out/bulk/All.trig

	@echo ""
	@echo "Now looking for any warnings or info:"
	@echo ""

	@# We don't want the build process to fail because of warnings/infos.
	@$(SHACL_CLI) --format table --shapes remote/shacl.ttl out/bulk/All.trig || true

bulk-ttl: $(BULK_TTL_FILES) remove-orphaned

jsonld: $(BULK_TTL_FILES)
	@$(MAKE) -f remote/split.mk jsonld

init:
	@$(MAKE) dockersetup 
	@$(MAKE) -f remote/split.mk init

all:
	@$(MAKE) init validate jsonld

define DELETE_UNEXPECTED_BULK_FILES
ifeq ($$(filter $$(file),$(EXPECTED_BULK_OUT_FILES)),) 
  $$(shell rm -f "$$(file)")
endif
endef

# Remove orphaned outputs which should no longer be present.
remove-orphaned: $(wildcard out/bulk/*.ttl) $(wildcard out/bulk/*.json) 
	$(foreach file,$^, $(eval $(DELETE_UNEXPECTED_BULK_FILES)))

clean:
	@$(MAKE) -f remote/split.mk clean
	@rm -rf out


.DEFAULT_GOAL := all

define CSVW_TO_TARGETS =
# Defines the target to convert a CSV-W into TTL
#  Importantly it makes sure that its local CSV files are listed as dependencies for make.
$(eval CSVW_FILE_NAME := $(shell basename "$(1)"))
$(eval TTL_FILE_$(1) := $(CSVW_FILE_NAME:%.csv-metadata.json=out/bulk/%.ttl))
$(eval CSVW_LOG_FILE_$(1) := $(CSVW_FILE_NAME:%.csv-metadata.json=out/validation/%.success.log))
$(eval CSVW_LOG_FILE_ERR_$(1) := $(CSVW_FILE_NAME:%.csv-metadata.json=out/validation/%.err.log))
$(eval CSVW_DIR_NAME_$(1) := $(shell dirname $$(realpath $(1))))

$(eval TABLE_SCHEMA_DEPENDENCIES_COMMAND_$(1) := cat "$(1)" \
			| $(JQ) '.tables[] | .tableSchema' \
			| sed 's/"\(.*\)"/\1/g' \
			| awk '{print "$(CSVW_DIR_NAME_$(1))/" $$$$0}' \
			| xargs -l realpath --canonicalize-missing --relative-to "$(WORKING_DIR)" \
			| xargs;)
$(eval TABLE_SCHEMA_DEPENDENCIES_$(1) = $(shell $(TABLE_SCHEMA_DEPENDENCIES_COMMAND_$(1)) ))

$(eval CSVCHECK_CSV_DEPENDENCIES_COMMAND_$(1) := cat "$(1)" \
			| $(JQ) '.tables[] | .url' \
			| sed 's/"\(.*\)"/\1/g' \
			| awk '{print "$(CSVW_DIR_NAME_$(1))/" $$$$0}' \
			| xargs -l realpath --canonicalize-missing --relative-to "$(WORKING_DIR)" \
			| xargs;)

$(eval CSVCHECK_CSV_DEPENDENCIES_$(1) = $(shell $(CSVCHECK_CSV_DEPENDENCIES_COMMAND_$(1)) ))


$(CSVW_LOG_FILE_$(1)): $(1) $(CSVCHECK_CSV_DEPENDENCIES_$(1)) $(TABLE_SCHEMA_DEPENDENCIES_$(1))
	@echo "=============================== Validating $$< ===============================" 
	@rm -f "$(CSVW_LOG_FILE_$(1))" "$(CSVW_LOG_FILE_ERR_$(1))"
	@RES=$$$$($(CSVW_CHECK) "$$<") && echo "$$$$RES" && touch "$(CSVW_LOG_FILE_$(1))" || (echo "$$$$RES" && echo "When validating $$<\n$$$$RES" > "$(CSVW_LOG_FILE_ERR_$(1))")
	@echo ""


$(eval CSV2RDF_CSV_DEPENDENCIES_COMMAND_$(1) := cat "$(1)" \
			| $(JQ) '.tables[] | select(.suppressOutput != true) | .url' \
			| sed 's/"\(.*\)"/\1/g' \
			| awk '{print "$(CSVW_DIR_NAME_$(1))/" $$$$0}' \
			| xargs -l realpath --canonicalize-missing --relative-to "$(WORKING_DIR)" \
			| xargs;)

$(eval CSV2RDF_CSV_DEPENDENCIES_$(1) = $(shell $(CSV2RDF_CSV_DEPENDENCIES_COMMAND_$(1)) ))

$(TTL_FILE_$(1)): $(1) $(CSV2RDF_CSV_DEPENDENCIES_$(1)) $(TABLE_SCHEMA_DEPENDENCIES_$(1)) out/validation/person-or-organization.csv
	@mkdir -p out/bulk
	@echo "=============================== Converting $$< to ttl $$@ ==============================="
	@# Unfortunately csv2rdf returns a non-zero status code if it produces no triples (even if this is to be expected).
	@# So for the time being we'll ignore any errors which come from it.
	@$$(CSV2RDF) "$$<" -o "$$@" || true
	@$$(CONVERT_LIST_VALUES_TO_NODES) "$$@"
	@echo "" 
endef


$(foreach file,$(CSVW_METADATA_FILES),$(eval $(call CSVW_TO_TARGETS,$(file))))
