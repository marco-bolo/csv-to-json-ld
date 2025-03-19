import pytest

from mbocsvwscripts.listcolumnforeignkeycheck import _get_invalid_list_column_values
from .utils import TEST_CASES_DIR


def test_list_column_foreign_key_failure():
    invalid_values = _get_invalid_list_column_values(
        TEST_CASES_DIR / "child_table_invalid.csv",
        "Associated Organizations",
        TEST_CASES_DIR / "parent_table.csv",
        "Known Organizations",
        separator="|",
    )

    assert invalid_values == {"Upperington Youth Orchestra", "Henry's Chocolate Club"}


def test_list_column_foreign_key_success():
    invalid_values = _get_invalid_list_column_values(
        TEST_CASES_DIR / "child_table_valid.csv",
        "Associated Organizations",
        TEST_CASES_DIR / "parent_table.csv",
        "Known Organizations",
        separator="|",
    )

    assert not any(invalid_values)


def test_list_column_foreign_key_success_comma_separator():
    invalid_values = _get_invalid_list_column_values(
        TEST_CASES_DIR / "child_table_valid_comma.csv",
        "Associated Organizations",
        TEST_CASES_DIR / "parent_table.csv",
        "Known Organizations",
        separator=",",
    )

    assert not any(invalid_values)


if __name__ == "__main__":
    pytest.main()
