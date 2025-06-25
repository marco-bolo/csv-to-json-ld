.PHONY: validate diagrams docs rebuild all

WORKING_DIR			:= $(shell pwd)
CURRENT_UID			:= $(shell id -u)
CLASSES				:= "Dataset" "PersonOrOrganization" "License" "VariableMeasured" "DataDownload" "DatasetComment"

LINKML_DOCKER			:= linkml/linkml:latest
MERMAID_CLI_DOCKER		:= minlag/mermaid-cli:latest

LINKML					:= docker run --rm -v "$(WORKING_DIR)":/work -w /work -u $(CURRENT_UID) $(LINKML_DOCKER) linkml
MERMAID_CLI				:= docker run --rm -v "$(WORKING_DIR)":/work -w /work -u $(CURRENT_UID) $(MERMAID_CLI_DOCKER)
MKDOCS					:= mkdocs

LINKML_SCHEMA_FILES		:= $(wildcard *.yaml)
MMD_FILES				:= $(CLASSES:"%"=diagrams/%.mmd)
SVG_FILES				:= $(CLASSES:"%"=diagrams/%.svg)


docker-pull:
	@docker pull "$(MERMAID_CLI_DOCKER)"
	@docker pull "$(LINKML_DOCKER)"

init: #docker-pull
	@mkdir -p diagrams
	@mkdir -p docs

validate: $(LINKML_SCHEMA_FILES)
	@$(foreach file,$(LINKML_SCHEMA_FILES), echo "======================> Validating $(file)\n"; \
		$(LINKML) lint --validate --ignore-warnings "$(file)"; \
		echo "\n"; \
	)

	# Sometimes the above just doesn't catch some errors. The following will catch more:
	@echo "======================> Testing docs generation (quick)"

	@$(LINKML) generate doc \
		--directory docs \
		--sort-by rank \
		--no-render-imports \
		--stacktrace \
		--no-use-slot-uris \
		--no-use-class-uris \
		--useuris \
		classes.yaml || rm -rf validating-docs-generation


	@rm -rf validating-docs-generation


$(MMD_FILES): $(LINKML_SCHEMA_FILES)
	@echo "Generating mermaid for $(@:mermaid-outputs/%=%)"; 
	@$(LINKML) generate erdiagram --format mermaid -c "$(@:diagrams/%.mmd=%)" --max-hops 0 classes.yaml > "$@";

diagrams/%.svg: diagrams/%.mmd
	@echo "Generating SVG for $<"
	@$(MERMAID_CLI) --input "$<" --output "$@";
	@docker run --rm -v "$(WORKING_DIR)":/work -w /work --entrypoint "/bin/sh" -u root $(MERMAID_CLI_DOCKER) -c 'chown -R $(CURRENT_UID):$(CURRENT_UID) "$@"'

diagrams: $(SVG_FILES)

markdown-docs: $(LINKML_SCHEMA_FILES)
	@echo "Generating Markdown Docs"
	@$(LINKML) generate doc \
		--directory docs \
		--sort-by rank \
		--no-render-imports \
		--stacktrace \
		--no-use-slot-uris \
		--no-use-class-uris \
		--useuris \
		classes.yaml 

docs: markdown-docs

	@echo "Injecting custom user guide docs..."
	@cp user-guide/*.md docs/

	$(eval DOCS := $(wildcard docs/*.md))
	@echo "Converting mermaid diagrams to SVG in Markdown docs"
	$(foreach doc,$(DOCS),$(MERMAID_CLI) -i "$(doc)" -o "$(doc)";)

	@echo "Building Mkdocs site"
	@$(MKDOCS) build

rebuild: clean init all

all: diagrams docs

clean:
	@rm -rf diagrams
	@rm -rf validating-docs-generation
	@rm -rf docs
	@rm -rf site

.DEFAULT_GOAL := all
