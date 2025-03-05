.PHONY: split clean output-directories init remove-orphaned

WORKING_DIR				:= $(shell pwd)
JENA_CLI_DOCKER			:= gsscogs/gss-jvm-build-tools:latest
MBO_TOOLS_DOCKER		:= ghcr.io/marco-bolo/csv-to-json-ld-tools:latest


RIOT					:= docker run --rm -v "$(WORKING_DIR)":/work -w /work $(JENA_CLI_DOCKER) riot
SPARQL					:= docker run --rm -v "$(WORKING_DIR)":/work -w /work $(JENA_CLI_DOCKER) sparql
JQ						:= docker run -i --rm -v "$(WORKING_DIR)":/work -w /work "$(MBO_TOOLS_DOCKER)" jq
JSONLD_CLI				:= docker run -i --rm -v "$(WORKING_DIR)":/work -w /work "$(MBO_TOOLS_DOCKER)" jsonld

SCHEMA_ORG_CONTEXT_URL 	:= https://schema.org/docs/jsonldcontext.json
SCHEMA_ORG_FILE			:= out/resources/schema-context.json

BULK_TTL_FILES 			:= $(wildcard out/bulk/*.ttl)
	
output-directories:
	@mkdir -p out/ttl
	@mkdir -p out/resources

$(SCHEMA_ORG_FILE):
	@curl --silent -H "Accept: application/json" --compressed --output "$(SCHEMA_ORG_FILE).tmp" "$(SCHEMA_ORG_CONTEXT_URL)";

	@# remove the `id` and `type` properties since compaction replaces `@id` with `id` and similarly for `@type`.
	@$(JQ) 'del(.["@context"].id) | del(.["@context"].type)' "$(SCHEMA_ORG_FILE).tmp" > "$(SCHEMA_ORG_FILE)";
	@rm -f "$(SCHEMA_ORG_FILE).tmp"

	@echo ""

init: output-directories $(SCHEMA_ORG_FILE)

out/%.json: out/ttl/%.ttl
	@echo "=============================== Converting $< to schema.org JSON-LD $@ ===============================" ;

	@# 1. We do a raw conversion of the TTL into JSON-LD
	@# 2. We change all https://schema.org/ URIs to http://schema.org/ in preparation for compaction 
	@# 		against the schema.org JSON-LD context (which uses exclusively http://schema.org URIs).
	@# 3. We now compact against the schema.org JSON-LD context so we can have things like `"@type": "Dataset"` 
	@# 		instead of `"@type": "https://schema.org/Dataset"`
	@# 4. Then we set the context to make use of the schema.org context, but tell it to use https URIs instead 
	@# 		of http.
	
	@$(RIOT) --syntax ttl --out json-ld "$<" \
		| sed 's/https:\/\/schema.org\//http:\/\/schema.org\//g' \
		| $(JSONLD_CLI) compact --context "$(SCHEMA_ORG_FILE)" --allow all \
		| $(JQ) '.["@context"] = { "@import": "https://schema.org/", "schema": "https://schema.org/" }' > "$@";

	@echo "";

define SPLIT_TTL =
# The following line is a bit of a beast.
# 	It creates a variable called `INDIVIDUAL_TTL_FILE_NAMES_$(1)` which is unique to each bulk TTL file.
# 	This is necessary so we don't get conflicting variables in the same scope.
#
#   Overall it queries the bulk TTL file for the unique subjects defined therein, pulls out the slug
#	from each of them and then converts that into an `out/ttl/file-name.ttl` which is where that subject's 
#	data will be placed. 
$(eval INDIVIDUAL_TTL_FILE_NAMES_$(1) = \
  $(shell $(SPARQL) --data "$(1)" --results tsv 'SELECT DISTINCT ?s WHERE { ?s ?p ?o .}' \
    | tail -n +2 \
	| cut -c 2- \
	| rev \
	| cut -c 2- \
	| rev \
	| xargs basename -a \
	| sed -e 's/^\(.*\)$$/out\/ttl\/\\\1.ttl/' \
	| xargs ))
$(eval SPLIT_TTL_FILES += $(INDIVIDUAL_TTL_FILE_NAMES_$(1)))

$(INDIVIDUAL_TTL_FILE_NAMES_$(1)) &: $(1)
	@echo "=============================== Splitting $(1) into $(INDIVIDUAL_TTL_FILE_NAMES_$(1)) ==============================="
	@$(foreach output_ttl_file,$(INDIVIDUAL_TTL_FILE_NAMES_$(1)), \
		file_name=$$$$(basename "$(output_ttl_file)"); \
		uri_stub=$$$$(echo "$$$${file_name%.ttl}"); \
		$(SPARQL) --data "$(1)" "prefix schema: <https://schema.org/> prefix goos: <https://goosocean.org/document/> prefix mbo: <https://w3id.org/marco-bolo/> CONSTRUCT {?s ?p ?o.} WHERE {?s ?p ?o. FILTER (STRENDS(STR(?s), \"$$$$uri_stub\")).}" > "$(output_ttl_file).tmp"; \
		$(RIOT) --syntax ttl --formatted ttl --check --strict "$(output_ttl_file).tmp" > "$(output_ttl_file)"; \
		rm -f "$(output_ttl_file).tmp"; \
		echo "$(output_ttl_file) complete." ;)
	@echo ""
endef

$(foreach file,$(BULK_TTL_FILES),$(eval $(call SPLIT_TTL,$(file))))

SPLIT_JSON_LD_FILES				:= $(SPLIT_TTL_FILES:out/ttl/%.ttl=out/%.json)
EXPECTED_INDIVIDUAL_OUT_FILES 	:= $(SPLIT_TTL_FILES) $(SPLIT_JSON_LD_FILES)


define DELETE_UNEXPECTED_INDIVIDUAL_FILES
ifeq ($$(filter $$(file),$(EXPECTED_INDIVIDUAL_OUT_FILES)),) 
  $$(shell rm -f "$$(file)")
endif
endef

# Remove orphaned outputs which should no longer be present.
remove-orphaned: $(wildcard out/*.json) $(wildcard out/ttl/*.ttl)
	$(foreach file,$^, $(eval $(DELETE_UNEXPECTED_INDIVIDUAL_FILES)))

ttl: $(SPLIT_TTL_FILES) remove-orphaned
jsonld: $(SPLIT_JSON_LD_FILES) remove-orphaned

clean:
	@rm -f $(SCHEMA_ORG_FILE)
	@rm -rf out/resources
	@rm -rf out/ttl
	@rm -f $(SPLIT_JSON_LD_FILES)

.DEFAULT_GOAL := jsonld