from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from mbocsvwscripts.unionuniqueidentifiers import _union_identifiers
from .utils import TEST_CASES_DIR


def test_mbo_list_columns_values_converted_to_node_references():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        unioned_file_out = tmp_dir / "a-and-b.csv"

        _union_identifiers(
            [TEST_CASES_DIR / "a.csv", TEST_CASES_DIR / "b.csv"],
            unioned_file_out,
            pid_column_name="MBO PID",
        )

        actual_df = pd.read_csv(unioned_file_out)
        expected_df = pd.DataFrame(
            {
                "MBO PID": [
                    "mbo_00000001",
                    "mbo_00000002",
                    "mbo_00000003",
                    "mbo_00000004",
                    "mbo_00000005",
                    "mbo_00000006",
                ]
            }
        )

        pd.testing.assert_frame_equal(expected_df, actual_df)


if __name__ == "__main__":
    pytest.main()
