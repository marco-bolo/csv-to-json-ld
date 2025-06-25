.PHONY: split clean output-directories init remove-orphaned

GIT_HASH			:= $(shell git rev-parse --verify HEAD)
GIT_HASH_REPO_URL	:= https://github.com/marco-bolo/csv-to-json-ld/tree/$(GIT_HASH)

WORKING_DIR				:= $(shell pwd)
UID						:= $(shell id -u)
GID						:= $(shell id -g)
JENA_CLI_DOCKER			:= gsscogs/gss-jvm-build-tools:latest
MBO_TOOLS_DOCKER		:= ghcr.io/marco-bolo/csv-to-json-ld-tools:latest


RIOT					:= docker run --rm -v "$(WORKING_DIR)":/work -u "$(UID)":"$(GID)" -w /work $(JENA_CLI_DOCKER) riot
SPARQL					:= docker run --rm -v "$(WORKING_DIR)":/work -u "$(UID)":"$(GID)" -w /work $(JENA_CLI_DOCKER) sparql
MBO_TOOLS_DOCKER_RUN	:= docker run -i --rm -v "$(WORKING_DIR)":/work -u "$(UID)":"$(GID)" -w /work "$(MBO_TOOLS_DOCKER)"
JQ						:= $(MBO_TOOLS_DOCKER_RUN) jq
JSONLD_CLI				:= $(MBO_TOOLS_DOCKER_RUN) jsonld
PARTITON_CLI			:= $(MBO_TOOLS_DOCKER_RUN) partition execute
PARTITON_LIST_CLI		:= $(MBO_TOOLS_DOCKER_RUN) partition list
PROCESS_PARA_METADATA	:= $(MBO_TOOLS_DOCKER_RUN) processparametadata


SCHEMA_ORG_CONTEXT_URL 	:= https://schema.org/docs/jsonldcontext.json
SCHEMA_ORG_FILE			:= out/resources/schema-context.json

BULK_TTL_FILES 			:= $(wildcard out/bulk/*.ttl)
	
output-directories:
	@mkdir -p out/raw-jsonld
	@mkdir -p out/resources

$(SCHEMA_ORG_FILE):
	@curl --silent -H "Accept: application/json" --compressed --output "$(SCHEMA_ORG_FILE).tmp" "$(SCHEMA_ORG_CONTEXT_URL)";

	@# remove the `id` and `type` properties since compaction replaces `@id` with `id` and similarly for `@type`.
	@$(JQ) 'del(.["@context"].id) | del(.["@context"].type)' "$(SCHEMA_ORG_FILE).tmp" > "$(SCHEMA_ORG_FILE)";
	@rm -f "$(SCHEMA_ORG_FILE).tmp"

	@echo ""

init: output-directories $(SCHEMA_ORG_FILE)

out/%.json: out/raw-jsonld/%.json
	@echo "=============================== Converting $< to schema.org JSON-LD $@ ===============================" ;

	@# 1. We do a raw conversion of the raw JSON-LD into tidier schema.org JSON-LD
	@# 2. We change all https://schema.org/ URIs to http://schema.org/ in preparation for compaction 
	@# 		against the schema.org JSON-LD context (which uses exclusively http://schema.org URIs).
	@# 3. We now compact against the schema.org JSON-LD context so we can have things like `"@type": "Dataset"` 
	@# 		instead of `"@type": "https://schema.org/Dataset"`
	@# 4. Then we set the context to make use of the schema.org context, but tell it to use https URIs instead 
	@# 		of http.

	@cat "$<" \
		| sed 's/https:\/\/schema.org\//http:\/\/schema.org\//g' \
		| $(JSONLD_CLI) compact --context "$(SCHEMA_ORG_FILE)" --allow all \
		| $(JQ) '.["@context"] = { "@import": "https://schema.org/", "schema": "https://schema.org/" }' > "$@";

	@echo "";

define SPLIT_TTL =
# The following line is a bit of a beast.
# 	It creates a variable called `INDIVIDUAL_RAW_JSON_LD_FILE_NAMES_$(1)` which is unique to each bulk TTL file.
# 	This is necessary so we don't get conflicting variables in the same scope.
#
#   Overall it queries the bulk TTL file for the unique subjects defined therein, pulls out the slug
#	from each of them and then converts that into an `out/raw-jsonld/file-name.json` which is where that subject's 
#	data will be placed. 
$(eval INDIVIDUAL_RAW_JSON_LD_FILE_NAMES_$(1) = \
  $(shell $(PARTITON_LIST_CLI) --out out/raw-jsonld "$(1)" ))
$(eval SPLIT_RAW_JSON_LD_FILES += $(INDIVIDUAL_RAW_JSON_LD_FILE_NAMES_$(1)) $(INDIVIDUAL_RAW_JSON_LD_FILE_NAMES_$(1):%.json=%-input-metadata.json))

$(INDIVIDUAL_RAW_JSON_LD_FILE_NAMES_$(1)) $(INDIVIDUAL_RAW_JSON_LD_FILE_NAMES_$(1):%.json=%-input-metadata.json)  &: $(1)
	@echo "=============================== Splitting $(1) into $(INDIVIDUAL_RAW_JSON_LD_FILE_NAMES_$(1)) and associated para-metadata files ==============================="
	@$(PARTITON_CLI) --out out/raw-jsonld "$(1)"
	@$(foreach file,$(INDIVIDUAL_RAW_JSON_LD_FILE_NAMES_$(1)),\
		$(eval INPUT_METADATA_FILE_$(file) := $(file:%.json=%-input-metadata.json)) \
		$(eval INPUT_METADATA_FILE_TMP_$(file) := $(file:%.json=%-input-metadata-tmp.json)) \
		$(PROCESS_PARA_METADATA) --git_repo_commit_file_url "$(GIT_HASH_REPO_URL)" "$(file)" "$(INPUT_METADATA_FILE_TMP_$(file))"; \
		$(JSONLD_CLI) frame --frame remote/para-metadata.frame.json "$(INPUT_METADATA_FILE_TMP_$(file))" > "$(INPUT_METADATA_FILE_$(file))"; \
		rm -f "$(INPUT_METADATA_FILE_TMP_$(file))"; \
	)
	@echo "Done".
	@echo ""


endef

$(foreach file,$(BULK_TTL_FILES),$(eval $(call SPLIT_TTL,$(file))))

TIDY_JSON_LD_FILES				:= $(SPLIT_RAW_JSON_LD_FILES:out/raw-jsonld/%=out/%)
EXPECTED_INDIVIDUAL_OUT_FILES 	:= $(TIDY_JSON_LD_FILES) $(SPLIT_RAW_JSON_LD_FILES)

define DELETE_UNEXPECTED_INDIVIDUAL_FILES
ifeq ($$(filter $$(file),$(EXPECTED_INDIVIDUAL_OUT_FILES)),) 
  $$(shell rm -f "$$(file)")
endif
endef

# Remove orphaned outputs which should no longer be present.
remove-orphaned: $(wildcard out/*.json) $(wildcard out/raw-jsonld/*.json) $(wildcard out/ttl/*.ttl) $(wildcard out/**/*-tmp.json)
	$(foreach file,$^, $(eval $(DELETE_UNEXPECTED_INDIVIDUAL_FILES)))

jsonld: $(TIDY_JSON_LD_FILES) remove-orphaned

clean:
	@rm -f $(SCHEMA_ORG_FILE)
	@rm -rf out/resources
	@rm -rf out/raw-jsonld
	@rm -f $(TIDY_JSON_LD_FILES)

.DEFAULT_GOAL := jsonld