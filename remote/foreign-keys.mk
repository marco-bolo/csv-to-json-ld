
MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT	:= Action.csv DataDownload.csv Dataset.csv DatasetComment.csv HowToStep.csv HowToTip.csv MonetaryGrant.csv Organization.csv Person.csv Place.csv PropertyValue.csv Service.csv SoftwareApplication.csv SoftwareSourceCode.csv
MANUAL_FOREIGN_KEY_VALIDATION_LOGS			:= $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT:%.csv=out/validation/%-csv-list-column-foreign-key.success.log)
MANUAL_FOREIGN_KEY_VALIDATION_LOGS_ERRORS	:= $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT:%.csv=out/validation/%-csv-list-column-foreign-key.err.log)

out/validation/Action-csv-list-column-foreign-key.success.log: Dataset.csv out/validation/person-or-organization.csv Action.csv HowTo.csv out/validation
	@rm -f "out/validation/Action-csv-list-column-foreign-key.err.log" "out/validation/Action-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in Action.csv['How To (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Action.csv" "How To (mPID)" "HowTo.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Action-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Action.csv['Participants (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Action.csv" "Participants (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Action-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Action.csv['Resulting Datasets (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Action.csv" "Resulting Datasets (mPIDs)" "Dataset.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Action-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Action.csv['Child Actions (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Action.csv" "Child Actions (mPIDs)" "Action.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Action-csv-list-column-foreign-key.err.log"

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
out/validation/DataDownload-csv-list-column-foreign-key.success.log: PublishingStatusDefinedTerm.csv License.csv out/validation/person-or-organization.csv Audience.csv out/validation
	@rm -f "out/validation/DataDownload-csv-list-column-foreign-key.err.log" "out/validation/DataDownload-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in DataDownload.csv['Publishing Status (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Publishing Status (mPID)" "PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in DataDownload.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in DataDownload.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in DataDownload.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in DataDownload.csv['Maintainer (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in DataDownload.csv['Publisher (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in DataDownload.csv['License (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "License (mPID)" "License.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in DataDownload.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "DataDownload.csv" "Audiences (mPIDs)" "Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/DataDownload-csv-list-column-foreign-key.err.log"

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
out/validation/Dataset-csv-list-column-foreign-key.success.log: Place.csv DataDownload.csv License.csv PropertyValue.csv Audience.csv out/validation/person-or-organization.csv PublishingStatusDefinedTerm.csv EmbargoStatement.csv Taxon.csv out/validation
	@rm -f "out/validation/Dataset-csv-list-column-foreign-key.err.log" "out/validation/Dataset-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in Dataset.csv['Contains Variables (PropertyValue mPIDs)*'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Contains Variables (PropertyValue mPIDs)*" "PropertyValue.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Taxa (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Taxa (mPIDs)" "Taxon.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Spatial Coverage (Place - mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Spatial Coverage (Place - mPID)" "Place.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Data Downloads (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Data Downloads (mPIDs)" "DataDownload.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Maintainer (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Publisher (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Publishing Status (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Publishing Status (mPID)" "PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Embargo Statement (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Embargo Statement (mPID)" "EmbargoStatement.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['License (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "License (mPID)" "License.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Dataset.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Dataset.csv" "Audiences (mPIDs)" "Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Dataset-csv-list-column-foreign-key.err.log"

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
	@echo "=============================== Validating values in DatasetComment.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "DatasetComment.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/DatasetComment-csv-list-column-foreign-key.err.log"

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
out/validation/HowToStep-csv-list-column-foreign-key.success.log: HowToTip.csv Audience.csv out/validation/person-or-organization.csv Service.csv SoftwareSourceCode.csv HowToStep.csv SoftwareApplication.csv out/validation
	@rm -f "out/validation/HowToStep-csv-list-column-foreign-key.err.log" "out/validation/HowToStep-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in HowToStep.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in HowToStep.csv['Provider (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Provider (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in HowToStep.csv['Source Code Citations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Source Code Citations (mPIDs)" "SoftwareSourceCode.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in HowToStep.csv['Software Application Citations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Software Application Citations (mPIDs)" "SoftwareApplication.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in HowToStep.csv['Service Citations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Service Citations (mPIDs)" "Service.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in HowToStep.csv['Child Steps (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Child Steps (mPIDs)" "HowToStep.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in HowToStep.csv['Implementation Tips (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Implementation Tips (mPIDs)" "HowToTip.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in HowToStep.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToStep.csv" "Audiences (mPIDs)" "Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToStep-csv-list-column-foreign-key.err.log"

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
out/validation/HowToTip-csv-list-column-foreign-key.success.log: Audience.csv out/validation
	@rm -f "out/validation/HowToTip-csv-list-column-foreign-key.err.log" "out/validation/HowToTip-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in HowToTip.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "HowToTip.csv" "Audiences (mPIDs)" "Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/HowToTip-csv-list-column-foreign-key.err.log"

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
out/validation/MonetaryGrant-csv-list-column-foreign-key.success.log: Organization.csv out/validation
	@rm -f "out/validation/MonetaryGrant-csv-list-column-foreign-key.err.log" "out/validation/MonetaryGrant-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in MonetaryGrant.csv['Funder Organizations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "MonetaryGrant.csv" "Funder Organizations (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/MonetaryGrant-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in MonetaryGrant.csv['Sponsor Organizations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "MonetaryGrant.csv" "Sponsor Organizations (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/MonetaryGrant-csv-list-column-foreign-key.err.log"

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
out/validation/Organization-csv-list-column-foreign-key.success.log: ContactPoint.csv Organization.csv MonetaryGrant.csv out/validation
	@rm -f "out/validation/Organization-csv-list-column-foreign-key.err.log" "out/validation/Organization-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in Organization.csv['Contact Points (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Organization.csv" "Contact Points (mPIDs)" "ContactPoint.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Organization-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Organization.csv['Parent Organization (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Organization.csv" "Parent Organization (mPID)" "Organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Organization-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Organization.csv['Member of Organizations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Organization.csv" "Member of Organizations (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Organization-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Organization.csv['Has Departments (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Organization.csv" "Has Departments (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Organization-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Organization.csv['Grants (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Organization.csv" "Grants (mPIDs)" "MonetaryGrant.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Organization-csv-list-column-foreign-key.err.log"

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
out/validation/Person-csv-list-column-foreign-key.success.log: ContactPoint.csv Organization.csv out/validation
	@rm -f "out/validation/Person-csv-list-column-foreign-key.err.log" "out/validation/Person-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in Person.csv['Works for Organizations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Person.csv" "Works for Organizations (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Person-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Person.csv['Affiliated to Organizations (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Person.csv" "Affiliated to Organizations (mPIDs)" "Organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Person-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Person.csv['Contact Points (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Person.csv" "Contact Points (mPIDs)" "ContactPoint.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Person-csv-list-column-foreign-key.err.log"

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
out/validation/Place-csv-list-column-foreign-key.success.log: GeoShape.csv out/validation
	@rm -f "out/validation/Place-csv-list-column-foreign-key.err.log" "out/validation/Place-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in Place.csv['GeoShape (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Place.csv" "GeoShape (mPID)" "GeoShape.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/Place-csv-list-column-foreign-key.err.log"

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
out/validation/PropertyValue-csv-list-column-foreign-key.success.log: PropertyValue.csv out/validation
	@rm -f "out/validation/PropertyValue-csv-list-column-foreign-key.err.log" "out/validation/PropertyValue-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in PropertyValue.csv['Is Sub-Type Of (PropertyValue mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "PropertyValue.csv" "Is Sub-Type Of (PropertyValue mPIDs)" "PropertyValue.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/PropertyValue-csv-list-column-foreign-key.err.log"

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
out/validation/Service-csv-list-column-foreign-key.success.log: Audience.csv Place.csv out/validation
	@rm -f "out/validation/Service-csv-list-column-foreign-key.err.log" "out/validation/Service-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in Service.csv['Audiences (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Service.csv" "Audiences (mPIDs)" "Audience.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Service-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in Service.csv['Places Served (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "Service.csv" "Places Served (mPIDs)" "Place.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/Service-csv-list-column-foreign-key.err.log"

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
out/validation/SoftwareApplication-csv-list-column-foreign-key.success.log: PublishingStatusDefinedTerm.csv out/validation/person-or-organization.csv out/validation
	@rm -f "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log" "out/validation/SoftwareApplication-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in SoftwareApplication.csv['Publishing Status (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Publishing Status (mPID)" "PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareApplication.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareApplication.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareApplication.csv['Maintainer (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareApplication.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareApplication.csv['Provider (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Provider (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareApplication.csv['Publisher (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareApplication.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareApplication-csv-list-column-foreign-key.err.log"

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
out/validation/SoftwareSourceCode-csv-list-column-foreign-key.success.log: PublishingStatusDefinedTerm.csv out/validation/person-or-organization.csv out/validation
	@rm -f "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log" "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.success.log"
	@echo "=============================== Validating values in SoftwareSourceCode.csv['Publishing Status (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Publishing Status (mPID)" "PublishingStatusDefinedTerm.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareSourceCode.csv['Author (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Author (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareSourceCode.csv['Contributors (mPIDs)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Contributors (mPIDs)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*" --separator "|") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareSourceCode.csv['Maintainer (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Maintainer (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareSourceCode.csv['Owner (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Owner (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"


	@echo "=============================== Validating values in SoftwareSourceCode.csv['Publisher (mPID)'] ==============================="
	@RES=$$($(LIST_COLUMN_FOREIGN_KEY_CHECK) "SoftwareSourceCode.csv" "Publisher (mPID)" "out/validation/person-or-organization.csv" "MBO Permanent Identifier*") && echo "$$RES" || echo "$$RES" >> "out/validation/SoftwareSourceCode-csv-list-column-foreign-key.err.log"

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
