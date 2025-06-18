import os
import pandas as pd

def load_csv(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename, dtype=str)
    return None

# Load valid Action IDs
action_df = load_csv("Action.csv")
valid_ids = set(action_df["id"].dropna()) if action_df is not None and "id" in action_df.columns else set()

# Files and columns to check
files_to_check = [
    ("Dataset.csv", "metadataDescribedForActionId"),
    ("Person.csv", "metadataDescribedForActionId"),
    ("Organization.csv", "metadataDescribedForActionId"),
    ("DefinedTerm.csv", "metadataDescribedForActionId"),
    ("ContactPoint.csv", "metadataDescribedForActionId"),
    ("License.csv", "metadataDescribedForActionId"),
    ("GeoShape.csv", "metadataDescribedForActionId"),
    ("Taxon.csv", "metadataDescribedForActionId"),
    ("Place.csv", "metadataDescribedForActionId"),
]

problems = []
for filename, column in files_to_check:
    df = load_csv(filename)
    if df is not None and column in df.columns:
        for i, val in df[column].dropna().items():
            if val not in valid_ids:
                problems.append((filename, i + 2, column, val))  # +2 for human-readable row

if problems:
    print("Invalid references found:\n")
    for f, r, c, v in problems:
        print(f"{f}, row {r}, column '{c}': value '{v}' not found in Action.csv")
    exit(1)
else:
    print("✅ All metadataDescribedForActionId values are valid.")

