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


MBO_CONTEXT_FILE		:= remote/mbo-context.json

BULK_TTL_FILES 			:= $(wildcard out/bulk/*.ttl)
	
output-directories:
	@mkdir -p out/raw-jsonld
	@mkdir -p out/resources

init: output-directories

out/%.json: out/raw-jsonld/%.json $(MBO_CONTEXT_FILE)
	@echo "=============================== Converting $< to schema.org JSON-LD $@ ===============================" ;

	@# We compact against our own context and then publish that same context inline.
	@# A document is therefore readable with exactly the context it declares: no remote
	@# fetch, no @import, and no http/https rewriting (csv2rdf already emits https URIs).

	@$(JSONLD_CLI) compact --context "$(MBO_CONTEXT_FILE)" --allow all "$<" \
		| $(JQ) --slurpfile ctx "$(MBO_CONTEXT_FILE)" '.["@context"] = $$ctx[0]["@context"]' > "$@";

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
	@echo "=============================== Splitting $(1) ==============================="
	@$(PARTITON_CLI) --out out/raw-jsonld "$(1)"
	@for file in $(INDIVIDUAL_RAW_JSON_LD_FILE_NAMES_$(1)); do \
		tmp_file="$$$${file%.json}-input-metadata-tmp.json"; \
		out_file="$$$${file%.json}-input-metadata.json"; \
		$(PROCESS_PARA_METADATA) --git_repo_commit_file_url "$(GIT_HASH_REPO_URL)" "$$$$file" "$$$$tmp_file"; \
		$(JSONLD_CLI) frame --frame remote/para-metadata.frame.json "$$$$tmp_file" > "$$$$out_file"; \
		rm -f "$$$$tmp_file"; \
	done
	@echo "Done."
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
	@rm -rf out/resources
	@rm -rf out/raw-jsonld
	@rm -f $(TIDY_JSON_LD_FILES)

.DEFAULT_GOAL := jsonld