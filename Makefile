
.PHONY: dockersetup output-directories jsonld clean bulk-ttl bulk-jsonld all init remove-orphaned

WORKING_DIR			:= $(shell pwd)

CSVW_CHECK_DOCKER	:= roblinksdata/csvw-check:latest
CSV2RDF_DOCKER		:= europe-west2-docker.pkg.dev/swirrl-devops-infrastructure-1/public/csv2rdf:v0.7.1
JENA_CLI_DOCKER		:= gsscogs/gss-jvm-build-tools:latest
MBO_TOOLS_DOCKER	:= ghcr.io/marco-bolo/csv-to-json-ld-tools:pr-16

CSVW_CHECK						:= docker run --rm -v "$(WORKING_DIR)":/work -w /work $(CSVW_CHECK_DOCKER) -s
CSV2RDF							:= docker run --rm -v "$(WORKING_DIR)":/work -w /work $(CSV2RDF_DOCKER) csv2rdf -m minimal -u 
RIOT							:= docker run --rm -v "$(WORKING_DIR)":/work -w /work $(JENA_CLI_DOCKER) riot
SPARQL							:= docker run --rm -v "$(WORKING_DIR)":/work -w /work $(JENA_CLI_DOCKER) sparql

MBO_TOOLS_DOCKER_RUN			:= docker run -i --rm -v "$(WORKING_DIR)":/work -w /work "$(MBO_TOOLS_DOCKER)"
CONVERT_LIST_VALUES_TO_NODES	:= $(MBO_TOOLS_DOCKER_RUN) listcolumnsasnodes
LIST_COLUMN_FOREIGN_KEY_CHECK	:= $(MBO_TOOLS_DOCKER_RUN) listcolumnforeignkeycheck
UNION_UNIQUE_IDENTIFIERS		:= $(MBO_TOOLS_DOCKER_RUN) unionuniqueidentifiers
JQ								:= $(MBO_TOOLS_DOCKER_RUN) jq
JSONLD_CLI						:= $(MBO_TOOLS_DOCKER_RUN) jsonld

CSVW_METADATA_FILES 			:= $(wildcard remote/*.csv-metadata.json)
CSVW_METADATA_VALIDATION_FILES	:= $(CSVW_METADATA_FILES:remote/%.csv-metadata.json=out/validation/%.log)
BULK_TTL_FILES    				:= $(CSVW_METADATA_FILES:remote/%.csv-metadata.json=out/bulk/%.ttl)
EXPECTED_BULK_OUT_FILES			:= $(BULK_TTL_FILES)
REFERENCED_CSVS_QUERY_FILE		:= remote/csvs-referenced-by-csvw.sparql

# Keep MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT up to date with the files it's necessary to perform list-column
# foreign key validation on.
MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT	:= dataset.csv organization.csv person.csv monetary-grant.csv
MANUAL_FOREIGN_KEY_VALIDATION_LOGS			:= $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT:%.csv=out/validation/%-csv-list-column-foreign-key.log)

dockersetup:
	@echo "=============================== Pulling & Building required docker images. ==============================="
	@docker pull $(CSVW_CHECK_DOCKER)
	@docker pull $(CSV2RDF_DOCKER)
	@docker pull $(JENA_CLI_DOCKER)
	@docker pull $(MBO_TOOLS_DOCKER)
	@echo "" ; 

output-directories:
	@mkdir -p out/bulk
	@mkdir -p out/validation

validate: $(CSVW_METADATA_VALIDATION_FILES) $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS)

out/validation/person-or-organization.csv: person.csv organization.csv
	@$(UNION_UNIQUE_IDENTIFIERS) --out out/validation/person-or-organization.csv person.csv organization.csv

out/validation/dataset-csv-list-column-foreign-key.log: dataset.csv variable-measured.csv data-download.csv
	@# Now we perform some more manual foreign key checks on the values inside particular list columns. 
	@# The detection of these could be automated in future, but they are so limited in scope at the moment that it probably isn't worth it.

	@echo "=============================== Validating values in dataset.csv['Variables Measured'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) dataset.csv "Variables Measured" variable-measured.csv "MBO PID" --separator "|"

	@echo "=============================== Validating values in dataset.csv['Distributions'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) dataset.csv "Distributions" data-download.csv "MBO Permanent Identifier" --separator "|"

	@echo "" > out/validation/dataset-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""


out/validation/organization-csv-list-column-foreign-key.log: organization.csv contact-point.csv monetary-grant.csv
	@echo "=============================== Validating values in organization.csv['Contact Point Ids'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) organization.csv "Contact Point Ids" contact-point.csv "MBO Permanent Identifier"	

	@# Now technically this one isn't a list column, but we're using the foreign key validation here since CSV-Ws don't support nullable 
	@# foreign key references. <https://github.com/roblinksdata/csvw-check/issues/2>
	@echo "=============================== Validating values in organization.csv['Parent Organization Id'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) organization.csv "Parent Organization Id" organization.csv "MBO Permanent Identifier"	

	@echo "=============================== Validating values in organization.csv['Member of Organization Ids'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) organization.csv "Member of Organization Ids" organization.csv "MBO Permanent Identifier"
	
	@echo "=============================== Validating values in organization.csv['Department Organization Ids'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) organization.csv "Department Organization Ids" organization.csv "MBO Permanent Identifier"
	
	@echo "=============================== Validating values in organization.csv['Funding Grant Ids'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) organization.csv "Funding Grant Ids" monetary-grant.csv "MBO Permanent Identifier"

	@echo "" > out/validation/organization-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""

out/validation/person-csv-list-column-foreign-key.log: person.csv organization.csv contact-point.csv
	@echo "=============================== Validating values in person.csv['Works For Organization Ids'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) person.csv "Works For Organization Ids" organization.csv "MBO Permanent Identifier"

	@echo "=============================== Validating values in person.csv['Affiliated Organization Ids'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) person.csv "Affiliated Organization Ids" organization.csv "MBO Permanent Identifier"

	@echo "=============================== Validating values in person.csv['Contact Point Ids'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) person.csv "Contact Point Ids" contact-point.csv "MBO Permanent Identifier"


	@echo "" > out/validation/person-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""	

out/validation/monetary-grant-csv-list-column-foreign-key.log: monetary-grant.csv organization.csv
	@echo "=============================== Validating values in monetary-grant.csv['Funder Organization Ids'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) monetary-grant.csv "Funder Organization Ids" organization.csv "MBO Permanent Identifier"

	@echo "=============================== Validating values in monetary-grant.csv['Sponsor Organization Ids'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) monetary-grant.csv "Sponsor Organization Ids" organization.csv "MBO Permanent Identifier"


	@echo "" > out/validation/monetary-grant-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""

out/bulk/%.json: out/bulk/%.ttl
	@echo "=============================== Converting $< to JSON-LD $@ ===============================" ;
	@$(RIOT) --syntax ttl --out json-ld "$<" > "$@";
	@echo "";

bulk-ttl: $(BULK_TTL_FILES) remove-orphaned

jsonld: $(BULK_TTL_FILES)
	@$(MAKE) -f split/Makefile jsonld

init:
	@$(MAKE) output-directories dockersetup 
	@$(MAKE) -f split/Makefile init

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

$(eval TABLE_SCHEMA_DEPENDENCIES_COMMAND_$(1) := cat "$(1)" \
			| $(JQ) '.tables[] | .tableSchema' \
			| sed 's/"\(.*\)"/\1/g' \
			| awk '{print "$(CSVW_DIR_NAME_$(1))/" $$$$0}' \
			| xargs -l realpath --relative-to "$(WORKING_DIR)" \
			| xargs;)
$(eval TABLE_SCHEMA_DEPENDENCIES_$(1) = $(shell $(TABLE_SCHEMA_DEPENDENCIES_COMMAND_$(1)) ))

$(eval CSVCHECK_CSV_DEPENDENCIES_COMMAND_$(1) := cat "$(1)" \
			| $(JQ) '.tables[] | .url' \
			| sed 's/"\(.*\)"/\1/g' \
			| awk '{print "$(CSVW_DIR_NAME_$(1))/" $$$$0}' \
			| xargs -l realpath -q --relative-to "$(WORKING_DIR)" \
			| xargs;)

$(eval CSVCHECK_CSV_DEPENDENCIES_$(1) = $(shell $(CSVCHECK_CSV_DEPENDENCIES_COMMAND_$(1)) ))


$(CSVW_LOG_FILE_$(1)): $(1) $(CSVCHECK_CSV_DEPENDENCIES_$(1)) $(TABLE_SCHEMA_DEPENDENCIES_$(1))
	@echo "=============================== Validating $$< ===============================" 
	@$(CSVW_CHECK) "$$<"
	@echo "" > "$(CSVW_LOG_FILE_$(1))"; # Let the build know that we've validated this file now.
	@echo ""


$(eval CSV2RDF_CSV_DEPENDENCIES_COMMAND_$(1) := cat "$(1)" \
			| $(JQ) '.tables[] | select(.suppressOutput != true) | .url' \
			| sed 's/"\(.*\)"/\1/g' \
			| awk '{print "$(CSVW_DIR_NAME_$(1))/" $$$$0}' \
			| xargs -l realpath -q --relative-to "$(WORKING_DIR)" \
			| xargs;)

$(eval CSV2RDF_CSV_DEPENDENCIES_$(1) = $(shell $(CSV2RDF_CSV_DEPENDENCIES_COMMAND_$(1)) ))

$(TTL_FILE_$(1)): $(1) $(CSV2RDF_CSV_DEPENDENCIES_$(1)) $(TABLE_SCHEMA_DEPENDENCIES_$(1))
	@echo "=============================== Converting $$< to ttl $$@ ==============================="
	@$$(CSV2RDF) "$$<" -o "$$@"
	@$$(CONVERT_LIST_VALUES_TO_NODES) "$$@"
	@echo "" 
endef


$(foreach file,$(CSVW_METADATA_FILES),$(eval $(call CSVW_TO_TARGETS,$(file))))
