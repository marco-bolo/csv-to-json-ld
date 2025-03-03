.PHONY: dockersetup output-directories jsonld clean bulk-ttl bulk-jsonld all init

WORKING_DIR			:= $(shell pwd)

CSVW_CHECK_DOCKER	:= roblinksdata/csvw-check:latest
CSV2RDF_DOCKER		:= europe-west2-docker.pkg.dev/swirrl-devops-infrastructure-1/public/csv2rdf:v0.7.1
JENA_CLI_DOCKER		:= gsscogs/gss-jvm-build-tools:latest

MBO_TOOLS_SCRIPTS_DIR	:= remote/scripts
MBO_TOOLS_DOCKER_FILE	:= $(MBO_TOOLS_SCRIPTS_DIR)/Dockerfile
MBO_TOOLS_DOCKER		:= mbo-tools

CSVW_CHECK						:= docker run --rm -v "$(WORKING_DIR)":/work -w /work $(CSVW_CHECK_DOCKER) -s
CSV2RDF							:= docker run --rm -v "$(WORKING_DIR)":/work -w /work $(CSV2RDF_DOCKER) csv2rdf -m minimal -u 
RIOT							:= docker run --rm -v "$(WORKING_DIR)":/work -w /work $(JENA_CLI_DOCKER) riot
SPARQL							:= docker run --rm -v "$(WORKING_DIR)":/work -w /work $(JENA_CLI_DOCKER) sparql

MBO_TOOLS_DOCKER_RUN			:= docker run -i --rm -v "$(WORKING_DIR)":/work -w /work "$(MBO_TOOLS_DOCKER)"
CONVERT_LIST_VALUES_TO_NODES	:= $(MBO_TOOLS_DOCKER_RUN) listcolumnsasnodes
LIST_COLUMN_FOREIGN_KEY_CHECK	:= $(MBO_TOOLS_DOCKER_RUN) listcolumnforeignkeycheck
JQ								:= $(MBO_TOOLS_DOCKER_RUN) jq
JSONLD_CLI						:= $(MBO_TOOLS_DOCKER_RUN) jsonld

CSVW_METADATA_FILES 			:= $(wildcard remote/*.csv-metadata.json)
CSVW_METADATA_VALIDATION_FILES	:= $(CSVW_METADATA_FILES:remote/%.csv-metadata.json=out/validation/%.log)
BULK_TTL_FILES    				:= $(CSVW_METADATA_FILES:remote/%.csv-metadata.json=out/bulk/%.ttl)
BULK_JSON_LD_FILES 				:= $(CSVW_METADATA_FILES:remote/%.csv-metadata.json=out/bulk/%.json)
REFERENCED_CSVS_QUERY_FILE		:= remote/csvs-referenced-by-csvw.sparql

dockersetup: $(MBO_TOOLS_DOCKER_FILE) $(MBO_TOOLS_SCRIPTS_DIR)
	@echo "=============================== Pulling & Building required docker images. ==============================="
	@docker pull $(CSVW_CHECK_DOCKER)
	@docker pull $(CSV2RDF_DOCKER)
	@docker pull $(JENA_CLI_DOCKER)
	@docker build -f "$(MBO_TOOLS_DOCKER_FILE)" -t "$(MBO_TOOLS_DOCKER)" "$(MBO_TOOLS_SCRIPTS_DIR)"
	@echo "" ; 

output-directories:
	@mkdir -p out/bulk
	@mkdir -p out/validation


validate: $(CSVW_METADATA_VALIDATION_FILES) out/validation/list-column-foreign-key-checks.log

out/validation/list-column-foreign-key-checks.log: dataset.csv variable-measured.csv
	@# Now we perform some more manual foreign key checks on the values inside particular list columns. 
	@# The detection of these could be automated in future, but they are so limited in scope at the moment that it probably isn't worth it.


	@echo "=============================== Validating values in dataset.csv['Variables Measured'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) dataset.csv "Variables Measured" variable-measured.csv "MBO PID" --separator "|"

	@echo "" > out/validation/list-column-foreign-key-checks.log # Let the build know we've done this validation now.
	@echo ""



out/bulk/%.json: out/bulk/%.ttl
	@echo "=============================== Converting $< to JSON-LD $@ ===============================" ;
	@$(RIOT) --syntax ttl --out json-ld "$<" > "$@";
	@echo "";

bulk-ttl: $(BULK_TTL_FILES)

bulk-jsonld: $(BULK_JSON_LD_FILES)

jsonld: $(BULK_TTL_FILES)
	@$(MAKE) -f split/Makefile jsonld

init:
	@$(MAKE) output-directories dockersetup 
	@$(MAKE) -f split/Makefile init

all:
	@$(MAKE) init validate bulk-jsonld jsonld

clean:
	@$(MAKE) -f split/Makefile clean
	@rm -rf out


.DEFAULT_GOAL := all

define CSVW_TO_TARGETS =
# Defines the target to convert a CSV-W into TTL
#  Importantly it makes sure that its local CSV files are listed as dependencies for make.
$(eval CSVW_FILE_NAME := $(shell basename "$(1)"))
$(eval TTL_FILE_$(1) := $(CSVW_FILE_NAME:%.csv-metadata.json=out/bulk/%.ttl))
$(eval CSVW_LOG_FILE_$(1) := $(CSVW_FILE_NAME:%.csv-metadata.json=out/validation/%.log))
$(eval CSVW_DIR_NAME_$(1) := $(shell dirname $$(realpath $(1))))

# $(eval INDIVIDUAL_CSV_DEPENDENCIES_COMMAND_$(1) := $(RIOT) --syntax jsonld --formatted ttl "$(1)" > "$(1).tmp.ttl"; \
# 		$(SPARQL) --data "$(1).tmp.ttl" --results tsv --query "$(REFERENCED_CSVS_QUERY_FILE)" \
# 			| tail -n +2 \
# 			| sed 's/"\(.*\)"/\1/g' \
# 			| awk '{print "$(CSVW_DIR_NAME_$(1))/" $$$$0}' \
# 			| xargs -l realpath --relative-to "$(WORKING_DIR)" \
# 			| xargs;)
# $(eval $(shell rm -rf "$(1).tmp.ttl"))
# The above using SPARQL is more general and correct, but the below using jq is far more performant and should meet our needs.

$(eval INDIVIDUAL_CSV_DEPENDENCIES_COMMAND_$(1) := cat "$(1)" \
			| $(JQ) '.tables[] | select(.suppressOutput != true) | .url' \
			| sed 's/"\(.*\)"/\1/g' \
			| awk '{print "$(CSVW_DIR_NAME_$(1))/" $$$$0}' \
			| xargs -l realpath --relative-to "$(WORKING_DIR)" \
			| xargs;)

$(eval INDIVIDUAL_CSV_DEPENDENCIES_$(1) = $(shell $(INDIVIDUAL_CSV_DEPENDENCIES_COMMAND_$(1)) ))

$(CSVW_LOG_FILE_$(1)): $(1) $(INDIVIDUAL_CSV_DEPENDENCIES_$(1))
	@echo "=============================== Validating $$< ===============================" 
	@$(CSVW_CHECK) "$$<"
	@echo "" > "$(CSVW_LOG_FILE_$(1))"; # Let the build know that we've validated this file now.
	@echo ""

$(TTL_FILE_$(1)): $(1) $(INDIVIDUAL_CSV_DEPENDENCIES_$(1))
	@echo "=============================== Converting $$< to ttl $$@ ==============================="
	@$$(CSV2RDF) "$$<" -o "$$@"
	@$$(CONVERT_LIST_VALUES_TO_NODES) "$$@"
	@echo "" 
endef


$(foreach file,$(CSVW_METADATA_FILES),$(eval $(call CSVW_TO_TARGETS,$(file))))
