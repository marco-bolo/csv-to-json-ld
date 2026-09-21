"""
listcolumnforeignkeycheck
-------------------------

Enforces foreign key constraints on the literal values inside list columns.
"""

import sys
from pathlib import Path
from typing import Set, Any, Optional

import click
import pandas as pd

_MBO_PID_URI_PREFIX = "https://w3id.org/marco-bolo/"


@click.command()
@click.argument(
    "csv_child_table",
    type=click.Path(exists=True),
)
@click.argument(
    "list_column_title_in_child_table",
    type=str,
)
@click.argument(
    "csv_parent_table",
    type=click.Path(exists=True),
)
@click.argument(
    "column_title_in_parent_table",
    type=str,
)
@click.option(
    "--separator",
    "-s",
    type=str,
    default="|",
    show_default=True,
    help="The character separating values in LIST_COLUMN_TITLE_IN_CHILD_TABLE",
)
@click.option(
    "--mbo-identifiers-only",
    is_flag=True,
    default=False,
    help="Only check values which name an MBO record, ignoring any other value. Use this for "
    "`(URL PIDs)` columns, which may legitimately hold any URL.",
)
def main(
    csv_child_table: click.Path,
    list_column_title_in_child_table: str,
    csv_parent_table: click.Path,
    column_title_in_parent_table: str,
    separator: str,
    mbo_identifiers_only: bool,
) -> None:
    """
    Validates the values of the `LIST_COLUMN_TITLE_IN_CHILD_TABLE` inside `CSV_CHILD_TABLE` against the authoritative
    values defined in `COLUMN_TITLE_IN_PARENT_TABLE` in `CSV_PARENT_TABLE`.
    """
    invalid_values = _get_invalid_list_column_values(
        Path(str(csv_child_table)),
        list_column_title_in_child_table,
        Path(str(csv_parent_table)),
        column_title_in_parent_table,
        separator,
        mbo_identifiers_only,
    )

    if any(invalid_values):
        print(
            f"Unexpected values found in {csv_child_table}['{list_column_title_in_child_table}'] but not in "
            f"{csv_parent_table}['{column_title_in_parent_table}']:\n{"\n".join([f"'{v}'" for v in invalid_values])}"
        )
        sys.exit(1)
    else:
        print(
            f"All values found in {csv_child_table}['{list_column_title_in_child_table}'] appear to be valid."
        )
        sys.exit(0)


def _get_invalid_list_column_values(
    csv_child_table: Path,
    list_column_title_in_child_table: str,
    csv_parent_table: Path,
    column_title_in_parent_table: str,
    separator: str,
    mbo_identifiers_only: bool = False,
) -> Set[Any]:
    """
    Returns missing values.
    """
    unique_child_values = _get_unique_child_table_values(
        csv_child_table, list_column_title_in_child_table, separator
    )
    unique_parent_values = _get_unique_parent_values(
        column_title_in_parent_table, csv_parent_table
    )

    if mbo_identifiers_only:
        unique_child_values = {
            identifier
            for identifier in (_as_mbo_identifier(str(v)) for v in unique_child_values)
            if identifier is not None
        }

    return unique_child_values - unique_parent_values


def _as_mbo_identifier(value: str) -> Optional[str]:
    """
    Returns the MBO identifier `value` names, or `None` where it does not name one.

    A `(URL PIDs)` column may hold any URL -- `https://example.com`, `doi:10.1000/example123` -- so
    most values in one are not ours to check. Those which are may be written either bare (`mbo_...`)
    or as the full PID URI, and the parent tables list the bare form, so the URI form is normalised
    to it. Without that normalisation the full-URI form would silently bypass this check, which is
    the bug this is here to prevent.
    """
    value = value.strip()
    if value.startswith(_MBO_PID_URI_PREFIX):
        value = value[len(_MBO_PID_URI_PREFIX) :]

    return value if value.startswith("mbo_") else None


def _get_unique_parent_values(column_title_in_parent_table, csv_parent_table):
    parent_table = pd.read_csv(csv_parent_table)
    parent_table_column = parent_table[column_title_in_parent_table]
    non_null_parent_values: pd.Series = parent_table_column[~parent_table_column.isnull()]  # type: ignore
    unique_parent_values = {str(value) for (_, value) in non_null_parent_values.items()}
    return unique_parent_values


def _get_unique_child_table_values(
    csv_child_table: Path, list_column_title_in_child_table: str, separator: str
) -> Set[Any]:
    child_table = pd.read_csv(csv_child_table)
    child_table_column = child_table[list_column_title_in_child_table]
    non_null_child_values: pd.Series = child_table_column[~child_table_column.isnull()]  # type: ignore
    return {
        individual_value
        for (_, cell_value) in non_null_child_values.items()
        for individual_value in str.split(str(cell_value), separator)
    }


if __name__ == "__main__":
    main()
