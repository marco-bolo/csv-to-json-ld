
.PHONY: dockersetup output-directories jsonld clean bulk-ttl bulk-jsonld all init remove-orphaned

WORKING_DIR			:= $(shell pwd)

CSVW_CHECK_DOCKER	:= roblinksdata/csvw-check:latest
CSV2RDF_DOCKER		:= europe-west2-docker.pkg.dev/swirrl-devops-infrastructure-1/public/csv2rdf:v0.7.1
JENA_CLI_DOCKER		:= gsscogs/gss-jvm-build-tools:latest
MBO_TOOLS_DOCKER	:= ghcr.io/marco-bolo/csv-to-json-ld-tools:latest

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

dockersetup:
	@echo "=============================== Pulling & Building required docker images. ==============================="
	@docker pull $(CSVW_CHECK_DOCKER)
	@docker pull $(CSV2RDF_DOCKER)
	@docker pull $(JENA_CLI_DOCKER)
	@docker pull $(MBO_TOOLS_DOCKER)
	@echo "" ; 

out/bulk: 
	@mkdir -p out/bulk

out/validation:
	@mkdir -p out/validation

out/validation/person-or-organization.csv: out/validation Person.csv Organization.csv 
	@$(UNION_UNIQUE_IDENTIFIERS) --out out/validation/person-or-organization.csv --column-name "MBO Permanent Identifier*" Person.csv Organization.csv

# BEGIN manual foreign key checks

# Keep MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT up to date with the files it's necessary to perform list-column
# foreign key validation on.
MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT	:= Action.csv DataDownload.csv Dataset.csv DatasetComment.csv HowToStep.csv HowToTip.csv MonetaryGrant.csv Organization.csv Person.csv Place.csv Service.csv SoftwareApplication.csv SoftwareSourceCode.csv
MANUAL_FOREIGN_KEY_VALIDATION_LOGS			:= $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT:%.csv=out/validation/%-csv-list-column-foreign-key.log)

out/validation/Action-csv-list-column-foreign-key.log: out/validation/person-or-organization.csv Dataset.csv Action.csv HowTo.csv out/validation
	@echo "=============================== Validating values in Action.csv['How To (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Action.csv" "How To (mPID)" "HowTo.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in Action.csv['Participants (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Action.csv" "Participants (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Action.csv['Resulting Datasets (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Action.csv" "Resulting Datasets (mPIDs)" "Dataset.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Action.csv['Child Actions (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Action.csv" "Child Actions (mPIDs)" "Action.csv" "MBO Permanent Identifier*" --separator "|"

	@echo "" > out/validation/Action-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/DataDownload-csv-list-column-foreign-key.log: PublishingStatusDefinedTerm.csv License.csv Dataset.csv out/validation/person-or-organization.csv Audience.csv out/validation
	@echo "=============================== Validating values in DataDownload.csv['Dataset (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Dataset (mPID)" "Dataset.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in DataDownload.csv['Publishing Status (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Publishing Status (mPID)" "PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in DataDownload.csv['Author (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in DataDownload.csv['Contributors (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in DataDownload.csv['Owner (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in DataDownload.csv['Maintainer (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in DataDownload.csv['Publisher (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in DataDownload.csv['License (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "License (mPID)" "License.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in DataDownload.csv['Audiences (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Audiences (mPIDs)" "Audience.csv" "MBO Permanent Identifier*" --separator "|"

	@echo "" > out/validation/DataDownload-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/Dataset-csv-list-column-foreign-key.log: PublishingStatusDefinedTerm.csv VariableMeasured.csv License.csv Place.csv DataDownload.csv out/validation/person-or-organization.csv EmbargoStatement.csv Audience.csv Taxon.csv out/validation
	@echo "=============================== Validating values in Dataset.csv['Variables Measured (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Variables Measured (mPIDs)" "VariableMeasured.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Dataset.csv['Taxa (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Taxa (mPIDs)" "Taxon.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Dataset.csv['Spatial Coverage (Place - mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Spatial Coverage (Place - mPID)" "Place.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in Dataset.csv['Distributions (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Distributions (mPIDs)" "DataDownload.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Dataset.csv['Author (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in Dataset.csv['Contributors (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Dataset.csv['Owner (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in Dataset.csv['Maintainer (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in Dataset.csv['Publisher (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in Dataset.csv['Publishing Status (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Publishing Status (mPID)" "PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in Dataset.csv['Embargo Statement (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Embargo Statement (mPID)" "EmbargoStatement.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in Dataset.csv['License (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "License (mPID)" "License.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in Dataset.csv['Audiences (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Audiences (mPIDs)" "Audience.csv" "MBO Permanent Identifier*" --separator "|"

	@echo "" > out/validation/Dataset-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/DatasetComment-csv-list-column-foreign-key.log: out/validation/person-or-organization.csv out/validation
	@echo "=============================== Validating values in DatasetComment.csv['Author (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "DatasetComment.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"

	@echo "" > out/validation/DatasetComment-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/HowToStep-csv-list-column-foreign-key.log: SoftwareSourceCode.csv Service.csv HowToStep.csv HowToTip.csv out/validation/person-or-organization.csv Audience.csv SoftwareApplication.csv out/validation
	@echo "=============================== Validating values in HowToStep.csv['Contributors (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in HowToStep.csv['Provider (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Provider (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in HowToStep.csv['Source Code Citations (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Source Code Citations (mPIDs)" "SoftwareSourceCode.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in HowToStep.csv['Software Application Citations (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Software Application Citations (mPIDs)" "SoftwareApplication.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in HowToStep.csv['Service Citations (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Service Citations (mPIDs)" "Service.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in HowToStep.csv['Child Steps (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Child Steps (mPIDs)" "HowToStep.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in HowToStep.csv['Implementation Tips (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Implementation Tips (mPIDs)" "HowToTip.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in HowToStep.csv['Audiences (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Audiences (mPIDs)" "Audience.csv" "MBO Permanent Identifier*" --separator "|"

	@echo "" > out/validation/HowToStep-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/HowToTip-csv-list-column-foreign-key.log: Audience.csv out/validation
	@echo "=============================== Validating values in HowToTip.csv['Audiences (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToTip.csv" "Audiences (mPIDs)" "Audience.csv" "MBO Permanent Identifier*" --separator "|"

	@echo "" > out/validation/HowToTip-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/MonetaryGrant-csv-list-column-foreign-key.log: Organization.csv out/validation
	@echo "=============================== Validating values in MonetaryGrant.csv['Funder Organizations (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "MonetaryGrant.csv" "Funder Organizations (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in MonetaryGrant.csv['Sponsor Organizations (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "MonetaryGrant.csv" "Sponsor Organizations (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|"

	@echo "" > out/validation/MonetaryGrant-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/Organization-csv-list-column-foreign-key.log: Organization.csv MonetaryGrant.csv ContactPoint.csv out/validation
	@echo "=============================== Validating values in Organization.csv['Contact Points (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Organization.csv" "Contact Points (mPIDs)" "ContactPoint.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Organization.csv['Parent Organization (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Organization.csv" "Parent Organization (mPID)" "Organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in Organization.csv['Member of Organizations (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Organization.csv" "Member of Organizations (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Organization.csv['Has Departments (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Organization.csv" "Has Departments (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Organization.csv['Grants (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Organization.csv" "Grants (mPIDs)" "MonetaryGrant.csv" "MBO Permanent Identifier*" --separator "|"

	@echo "" > out/validation/Organization-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/Person-csv-list-column-foreign-key.log: Organization.csv ContactPoint.csv out/validation
	@echo "=============================== Validating values in Person.csv['Works for Organizations (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Person.csv" "Works for Organizations (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Person.csv['Affiliated to Organizations (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Person.csv" "Affiliated to Organizations (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Person.csv['Contact Points (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Person.csv" "Contact Points (mPIDs)" "ContactPoint.csv" "MBO Permanent Identifier*" --separator "|"

	@echo "" > out/validation/Person-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/Place-csv-list-column-foreign-key.log: GeoShape.csv out/validation
	@echo "=============================== Validating values in Place.csv['GeoShape (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Place.csv" "GeoShape (mPID)" "GeoShape.csv" "MBO Permanent Identifier*"

	@echo "" > out/validation/Place-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/Service-csv-list-column-foreign-key.log: Audience.csv Place.csv out/validation
	@echo "=============================== Validating values in Service.csv['Audiences (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Service.csv" "Audiences (mPIDs)" "Audience.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in Service.csv['Places Served (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "Service.csv" "Places Served (mPIDs)" "Place.csv" "MBO Permanent Identifier*" --separator "|"

	@echo "" > out/validation/Service-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/SoftwareApplication-csv-list-column-foreign-key.log: PublishingStatusDefinedTerm.csv out/validation/person-or-organization.csv out/validation
	@echo "=============================== Validating values in SoftwareApplication.csv['Publishing Status (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Publishing Status (mPID)" "PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in SoftwareApplication.csv['Author (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in SoftwareApplication.csv['Contributors (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in SoftwareApplication.csv['Maintainer (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in SoftwareApplication.csv['Owner (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in SoftwareApplication.csv['Provider (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Provider (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in SoftwareApplication.csv['Publisher (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"

	@echo "" > out/validation/SoftwareApplication-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""
out/validation/SoftwareSourceCode-csv-list-column-foreign-key.log: PublishingStatusDefinedTerm.csv out/validation/person-or-organization.csv out/validation
	@echo "=============================== Validating values in SoftwareSourceCode.csv['Publishing Status (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Publishing Status (mPID)" "PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in SoftwareSourceCode.csv['Author (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in SoftwareSourceCode.csv['Contributors (mPIDs)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|"


	@echo "=============================== Validating values in SoftwareSourceCode.csv['Maintainer (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in SoftwareSourceCode.csv['Owner (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"


	@echo "=============================== Validating values in SoftwareSourceCode.csv['Publisher (mPID)'] ==============================="
	@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*"

	@echo "" > out/validation/SoftwareSourceCode-csv-list-column-foreign-key.log # Let the build know we've done this validation now.
	@echo ""

# END manual foreign key checks

validate: $(CSVW_METADATA_VALIDATION_FILES) $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS)

out/bulk/%.json: out/bulk/%.ttl
	@echo "=============================== Converting $< to JSON-LD $@ ===============================" ;
	@$(RIOT) --syntax ttl --out json-ld "$<" > "$@";
	@echo "";

bulk-ttl: $(BULK_TTL_FILES) remove-orphaned

jsonld: $(BULK_TTL_FILES)
	@$(MAKE) -f split/Makefile jsonld

init:
	@$(MAKE) dockersetup 
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
	@$(CSVW_CHECK) "$$<"
	@echo "" > "$(CSVW_LOG_FILE_$(1))"; # Let the build know that we've validated this file now.
	@echo ""


$(eval CSV2RDF_CSV_DEPENDENCIES_COMMAND_$(1) := cat "$(1)" \
			| $(JQ) '.tables[] | select(.suppressOutput != true) | .url' \
			| sed 's/"\(.*\)"/\1/g' \
			| awk '{print "$(CSVW_DIR_NAME_$(1))/" $$$$0}' \
			| xargs -l realpath --canonicalize-missing --relative-to "$(WORKING_DIR)" \
			| xargs;)

$(eval CSV2RDF_CSV_DEPENDENCIES_$(1) = $(shell $(CSV2RDF_CSV_DEPENDENCIES_COMMAND_$(1)) ))

$(TTL_FILE_$(1)): $(1) $(CSV2RDF_CSV_DEPENDENCIES_$(1)) $(TABLE_SCHEMA_DEPENDENCIES_$(1)) out/bulk out/validation/person-or-organization.csv
	@echo "=============================== Converting $$< to ttl $$@ ==============================="
	@# Unfortunately csv2rdf returns a non-zero status code if it produces no triples (even if this is to be expected).
	@# So for the time being we'll ignore any errors which come from it.
	@$$(CSV2RDF) "$$<" -o "$$@" || true
	@$$(CONVERT_LIST_VALUES_TO_NODES) "$$@"
	@echo "" 
endef


$(foreach file,$(CSVW_METADATA_FILES),$(eval $(call CSVW_TO_TARGETS,$(file))))
