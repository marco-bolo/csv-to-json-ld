
MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT	:= Action.csv DataDownload.csv Dataset.csv DatasetComment.csv Document.csv HowTo.csv HowToStep.csv HowToTip.csv Instrument.csv MonetaryGrant.csv Organization.csv Person.csv Place.csv Platform.csv PropertyValue.csv Service.csv SoftwareApplication.csv SoftwareSourceCode.csv
MANUAL_FOREIGN_KEY_VALIDATION_LOGS			:= $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT:%.csv=out/validation/%-csv-list-column-foreign-key.success.log)
MANUAL_FOREIGN_KEY_VALIDATION_LOGS_ERRORS	:= $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT:%.csv=out/validation/%-csv-list-column-foreign-key.err.log)

out/validation/Action-csv-list-column-foreign-key.success.log: data/Dataset.csv out/validation/person-or-organization.csv data/Action.csv data/HowTo.csv out/validation
	@rm -f "out/validation/Action-csv-list-column-foreign-key.err.log" "out/validation/Action-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/Action.csv['How To (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Action.csv" "How To (mPID)" "data/HowTo.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Action-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Action.csv['Participants (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Action.csv" "Participants (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Action-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Action.csv['Resulting Datasets (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Action.csv" "Resulting Datasets (mPIDs)" "data/Dataset.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Action-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Action.csv['Child Actions (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Action.csv" "Child Actions (mPIDs)" "data/Action.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Action-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/Action-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/Action-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/Action-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/DataDownload-csv-list-column-foreign-key.success.log: data/Audience.csv data/PublishingStatusDefinedTerm.csv out/validation/person-or-organization.csv data/License.csv out/validation
	@rm -f "out/validation/DataDownload-csv-list-column-foreign-key.err.log" "out/validation/DataDownload-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/DataDownload.csv['Publishing Status (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/DataDownload.csv" "Publishing Status (mPID)" "data/PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/DataDownload.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/DataDownload.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/DataDownload.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/DataDownload.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/DataDownload.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/DataDownload.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/DataDownload.csv['Maintainer (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/DataDownload.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/DataDownload.csv['Publisher (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/DataDownload.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/DataDownload.csv['License (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/DataDownload.csv" "License (mPID)" "data/License.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/DataDownload.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/DataDownload.csv" "Audiences (mPIDs)" "data/Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/DataDownload-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/DataDownload-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/DataDownload-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/Dataset-csv-list-column-foreign-key.success.log: out/validation/person-or-organization.csv data/PropertyValue.csv data/Taxon.csv data/PublishingStatusDefinedTerm.csv data/Audience.csv data/EmbargoStatement.csv data/Place.csv data/DataDownload.csv data/License.csv out/validation
	@rm -f "out/validation/Dataset-csv-list-column-foreign-key.err.log" "out/validation/Dataset-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/Dataset.csv['Contains Variables (PropertyValue mPIDs)*'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Contains Variables (PropertyValue mPIDs)*" "data/PropertyValue.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Taxa (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Taxa (mPIDs)" "data/Taxon.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Spatial Coverage (Place - mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Spatial Coverage (Place - mPID)" "data/Place.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Data Downloads (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Data Downloads (mPIDs)" "data/DataDownload.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Maintainer (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Publisher (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Publishing Status (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Publishing Status (mPID)" "data/PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Embargo Statement (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Embargo Statement (mPID)" "data/EmbargoStatement.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['License (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "License (mPID)" "data/License.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Dataset.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Dataset.csv" "Audiences (mPIDs)" "data/Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/Dataset-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/Dataset-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/Dataset-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/DatasetComment-csv-list-column-foreign-key.success.log: out/validation/person-or-organization.csv out/validation
	@rm -f "out/validation/DatasetComment-csv-list-column-foreign-key.err.log" "out/validation/DatasetComment-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/DatasetComment.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/DatasetComment.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/DatasetComment-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/DatasetComment-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/DatasetComment-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/DatasetComment-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/Document-csv-list-column-foreign-key.success.log: out/validation/person-or-organization.csv data/Taxon.csv data/PublishingStatusDefinedTerm.csv data/Audience.csv data/EmbargoStatement.csv data/Place.csv data/License.csv out/validation
	@rm -f "out/validation/Document-csv-list-column-foreign-key.err.log" "out/validation/Document-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/Document.csv['Taxa (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "Taxa (mPIDs)" "data/Taxon.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Document.csv['Spatial Coverage (Place - mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "Spatial Coverage (Place - mPID)" "data/Place.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Document.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "Audiences (mPIDs)" "data/Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Document.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Document.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Document.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Document.csv['Maintainer (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Document.csv['Publisher (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Document.csv['Publishing Status (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "Publishing Status (mPID)" "data/PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Document.csv['License (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "License (mPID)" "data/License.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Document.csv['Embargo Statement (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Document.csv" "Embargo Statement (mPID)" "data/EmbargoStatement.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Document-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/Document-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/Document-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/Document-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/HowTo-csv-list-column-foreign-key.success.log: data/Service.csv out/validation
	@rm -f "out/validation/HowTo-csv-list-column-foreign-key.err.log" "out/validation/HowTo-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/HowTo.csv['Document Citations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowTo.csv" "Document Citations (mPIDs)" "data/Service.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowTo-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/HowTo-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/HowTo-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/HowTo-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/HowToStep-csv-list-column-foreign-key.success.log: data/SoftwareApplication.csv out/validation/person-or-organization.csv data/SoftwareSourceCode.csv data/Audience.csv data/Instrument.csv data/HowToTip.csv data/Service.csv data/HowToStep.csv data/Platform.csv out/validation
	@rm -f "out/validation/HowToStep-csv-list-column-foreign-key.err.log" "out/validation/HowToStep-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/HowToStep.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/HowToStep.csv['Provider (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Provider (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/HowToStep.csv['Source Code Citations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Source Code Citations (mPIDs)" "data/SoftwareSourceCode.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/HowToStep.csv['Software Application Citations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Software Application Citations (mPIDs)" "data/SoftwareApplication.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/HowToStep.csv['Service Citations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Service Citations (mPIDs)" "data/Service.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/HowToStep.csv['Document Citations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Document Citations (mPIDs)" "data/Service.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/HowToStep.csv['Child Steps (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Child Steps (mPIDs)" "data/HowToStep.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/HowToStep.csv['Implementation Tips (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Implementation Tips (mPIDs)" "data/HowToTip.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/HowToStep.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Audiences (mPIDs)" "data/Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/HowToStep.csv['Platforms Used (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Platforms Used (mPIDs)" "data/Platform.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/HowToStep.csv['Instruments Used (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToStep.csv" "Instruments Used (mPIDs)" "data/Instrument.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/HowToStep-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/HowToStep-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/HowToStep-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/HowToTip-csv-list-column-foreign-key.success.log: data/Audience.csv out/validation
	@rm -f "out/validation/HowToTip-csv-list-column-foreign-key.err.log" "out/validation/HowToTip-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/HowToTip.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/HowToTip.csv" "Audiences (mPIDs)" "data/Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToTip-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/HowToTip-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/HowToTip-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/HowToTip-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/Instrument-csv-list-column-foreign-key.success.log: data/Document.csv out/validation/person-or-organization.csv data/Platform.csv out/validation
	@rm -f "out/validation/Instrument-csv-list-column-foreign-key.err.log" "out/validation/Instrument-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/Instrument.csv['Mounted On Platform (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Instrument.csv" "Mounted On Platform (mPID)" "data/Platform.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Instrument-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Instrument.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Instrument.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Instrument-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Instrument.csv['Maintainer (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Instrument.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Instrument-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Instrument.csv['Described By Documents (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Instrument.csv" "Described By Documents (mPIDs)" "data/Document.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Instrument-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/Instrument-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/Instrument-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/Instrument-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/MonetaryGrant-csv-list-column-foreign-key.success.log: data/Organization.csv out/validation
	@rm -f "out/validation/MonetaryGrant-csv-list-column-foreign-key.err.log" "out/validation/MonetaryGrant-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/MonetaryGrant.csv['Funder Organizations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/MonetaryGrant.csv" "Funder Organizations (mPIDs)" "data/Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/MonetaryGrant-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/MonetaryGrant.csv['Sponsor Organizations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/MonetaryGrant.csv" "Sponsor Organizations (mPIDs)" "data/Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/MonetaryGrant-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/MonetaryGrant-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/MonetaryGrant-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/MonetaryGrant-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/Organization-csv-list-column-foreign-key.success.log: data/Organization.csv data/MonetaryGrant.csv data/ContactPoint.csv out/validation
	@rm -f "out/validation/Organization-csv-list-column-foreign-key.err.log" "out/validation/Organization-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/Organization.csv['Contact Points (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Organization.csv" "Contact Points (mPIDs)" "data/ContactPoint.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Organization-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Organization.csv['Parent Organization (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Organization.csv" "Parent Organization (mPID)" "data/Organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Organization-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Organization.csv['Member of Organizations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Organization.csv" "Member of Organizations (mPIDs)" "data/Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Organization-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Organization.csv['Has Departments (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Organization.csv" "Has Departments (mPIDs)" "data/Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Organization-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Organization.csv['Grants (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Organization.csv" "Grants (mPIDs)" "data/MonetaryGrant.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Organization-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/Organization-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/Organization-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/Organization-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/Person-csv-list-column-foreign-key.success.log: data/Organization.csv data/ContactPoint.csv out/validation
	@rm -f "out/validation/Person-csv-list-column-foreign-key.err.log" "out/validation/Person-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/Person.csv['Works for Organizations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Person.csv" "Works for Organizations (mPIDs)" "data/Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Person-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Person.csv['Affiliated to Organizations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Person.csv" "Affiliated to Organizations (mPIDs)" "data/Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Person-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Person.csv['Contact Points (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Person.csv" "Contact Points (mPIDs)" "data/ContactPoint.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Person-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/Person-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/Person-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/Person-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/Place-csv-list-column-foreign-key.success.log: data/GeoShape.csv out/validation
	@rm -f "out/validation/Place-csv-list-column-foreign-key.err.log" "out/validation/Place-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/Place.csv['GeoShape (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Place.csv" "GeoShape (mPID)" "data/GeoShape.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Place-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/Place-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/Place-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/Place-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/Platform-csv-list-column-foreign-key.success.log: data/Document.csv data/Organization.csv out/validation/person-or-organization.csv out/validation
	@rm -f "out/validation/Platform-csv-list-column-foreign-key.err.log" "out/validation/Platform-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/Platform.csv['Operator Organization (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Platform.csv" "Operator Organization (mPID)" "data/Organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Platform-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Platform.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Platform.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Platform-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Platform.csv['Described By Documents (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Platform.csv" "Described By Documents (mPIDs)" "data/Document.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Platform-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/Platform-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/Platform-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/Platform-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/PropertyValue-csv-list-column-foreign-key.success.log: data/PropertyValue.csv out/validation
	@rm -f "out/validation/PropertyValue-csv-list-column-foreign-key.err.log" "out/validation/PropertyValue-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/PropertyValue.csv['Is Sub-Type Of (PropertyValue mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/PropertyValue.csv" "Is Sub-Type Of (PropertyValue mPIDs)" "data/PropertyValue.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/PropertyValue-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/PropertyValue-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/PropertyValue-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/PropertyValue-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/Service-csv-list-column-foreign-key.success.log: data/Place.csv data/Audience.csv out/validation
	@rm -f "out/validation/Service-csv-list-column-foreign-key.err.log" "out/validation/Service-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/Service.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Service.csv" "Audiences (mPIDs)" "data/Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Service-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/Service.csv['Places Served (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/Service.csv" "Places Served (mPIDs)" "data/Place.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Service-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/Service-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/Service-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/Service-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/SoftwareApplication-csv-list-column-foreign-key.success.log: data/PublishingStatusDefinedTerm.csv out/validation/person-or-organization.csv out/validation
	@rm -f "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log" "out/validation/SoftwareApplication-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/SoftwareApplication.csv['Publishing Status (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareApplication.csv" "Publishing Status (mPID)" "data/PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareApplication.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareApplication.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareApplication.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareApplication.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareApplication.csv['Maintainer (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareApplication.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareApplication.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareApplication.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareApplication.csv['Provider (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareApplication.csv" "Provider (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareApplication.csv['Publisher (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareApplication.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/SoftwareApplication-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
out/validation/SoftwareSourceCode-csv-list-column-foreign-key.success.log: data/PublishingStatusDefinedTerm.csv out/validation/person-or-organization.csv out/validation
	@rm -f "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log" "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in data/SoftwareSourceCode.csv['Publishing Status (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareSourceCode.csv" "Publishing Status (mPID)" "data/PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareSourceCode.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareSourceCode.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareSourceCode.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareSourceCode.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareSourceCode.csv['Maintainer (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareSourceCode.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareSourceCode.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareSourceCode.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in data/SoftwareSourceCode.csv['Publisher (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "data/SoftwareSourceCode.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"

	@if [ -f "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log" ]; then \
	   echo ""; \
	   printf '[0;31m'; # Red \
	   echo "Foreign Key errors detected:"; \
	   cat "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"; \
	   printf '[0m'; # Reset colour \
	 else \
	   touch "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.success.log"; \
	 fi
	@echo ""
