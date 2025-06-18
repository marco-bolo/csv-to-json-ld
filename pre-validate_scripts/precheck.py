import csv
from pathlib import Path
from collections import defaultdict

# Define expected foreign key dependencies
DEPENDENCIES = {
    "Dataset.csv": {
        "metadataDescribedForActionId": "Action.csv",
        "metadataPublisherId": ["Person.csv", "Organization.csv"]
    },
    "DataDownload.csv": {
        "datasetMboId": "Dataset.csv",
        "metadataPublisherId": ["Person.csv", "Organization.csv"]
    },
    "Person.csv": {
        "metadataPublisherId": ["Person.csv", "Organization.csv"]
    },
    "Organization.csv": {
        "metadataPublisherId": ["Person.csv", "Organization.csv"]
    },
    # Add more as needed
}

def load_ids(filepath):
    """Return a set of IDs from a CSV file with 'id' column."""
    try:
        with open(filepath, newline='') as f:
            reader = csv.DictReader(f)
            return {row["id"] for row in reader if "id" in row}
    except Exception as e:
        print(f"⚠️  Skipping {filepath}: {e}")
        return set()

def validate_foreign_keys():
    base_path = Path(".")
    all_ids = defaultdict(set)

    # Preload all ID sets
    for file in base_path.glob("*.csv"):
        ids = load_ids(file)
        if ids:
            all_ids[file.name] = ids

    # Run validations
    print("🔍 Checking foreign key references...\n")
    has_error = False
    for source_file, rules in DEPENDENCIES.items():
        source_path = base_path / source_file
        if not source_path.exists():
            continue

        with open(source_path, newline='') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):  # header is line 1
                for field, targets in rules.items():
                    if isinstance(targets, str):
                        targets = [targets]

                    value = row.get(field, "").strip()
                    if not value:
                        continue

                    for val in value.split("|"):  # support multivalue fields
                        val = val.strip()
                        if not val:
                            continue

                        if not any(val in all_ids[t] for t in targets):
                            print(f"❌ {source_file}, line {i}: {field} value '{val}' not found in {targets}")
                            has_error = True

    if not has_error:
        print("\n✅ All foreign key checks passed.")
    else:
        print("\n❌ Some foreign key errors found.")

if __name__ == "__main__":
    validate_foreign_keys()
