"""
unionuniqueidentifiers
----------------------

There are some schema.org predicates which support referencing multiple distinct types,
    e.g. https://schema.org/funder allows you to point to a `schema:Organization` or a `schema:Person`.

This script takes the `organization.csv` and `person.csv` files and generates a CSV file containing the
complete set of permitted MBO identifiers for both of these types. We can then point to that and enforce
foreign key constraints.
"""

from typing import Tuple, List, Set

import click


@click.command()
@click.option("-o", "--out", required=True, type=click.Path(exists=False))
@click.argument("csv_files", type=click.Path(exists=True), nargs=-1)
def main(out: click.Path, csv_files: Tuple[click.Path, ...]):
    """
    Do the thing please.

    N.B. This script is dumb and requires that the MBO PID column is the first column in all
    input CSV files.
    """
    _union_identifiers([Path(str(p)) for p in csv_files], Path(str(out)))


from pathlib import Path


import pandas as pd


def _union_identifiers(csv_files: List[Path], out_file: Path) -> None:
    mbo_identifiers: Set[str] = set()
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        mbo_identifiers |= set(df[df.columns[0]])

    df_out = pd.DataFrame({"MBO PID": sorted(mbo_identifiers)})
    df_out.to_csv(out_file, index=False)


if __name__ == "__main__":
    main()
