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


def test_url_pids_column_ignores_values_which_are_not_ours():
    """
    A `(URL PIDs)` column may hold any URL, so only the values naming an MBO record are checked.
    Without `--mbo-identifiers-only` every external URL would be reported as a broken reference.
    """
    invalid_values = _get_invalid_list_column_values(
        TEST_CASES_DIR / "url_pids_child_table.csv",
        "Based On (URL PIDs)",
        TEST_CASES_DIR / "all_identifiers.csv",
        "MBO Permanent Identifier*",
        separator="|",
        mbo_identifiers_only=True,
    )

    assert "https://example.com/someone-elses-dataset" not in invalid_values
    assert "doi:10.1000/example123" not in invalid_values
    assert "ftp://ftp.example.org/data" not in invalid_values


def test_url_pids_column_catches_reference_to_missing_record():
    """This is the class of bug which published `file:///work/out/bulk/mbo_...` - see issue #337."""
    invalid_values = _get_invalid_list_column_values(
        TEST_CASES_DIR / "url_pids_child_table.csv",
        "Based On (URL PIDs)",
        TEST_CASES_DIR / "all_identifiers.csv",
        "MBO Permanent Identifier*",
        separator="|",
        mbo_identifiers_only=True,
    )

    assert "mbo_typo_not_in_catalogue" in invalid_values


def test_url_pids_column_catches_missing_record_written_as_a_full_pid_uri():
    """
    Both forms name a record, and the catalogue is listed in the bare form. Were the URI form not
    normalised it would be skipped as "not ours" and bypass the check entirely - the same bug in a
    new coat. In the real data this doubles the number of values actually checked.
    """
    invalid_values = _get_invalid_list_column_values(
        TEST_CASES_DIR / "url_pids_child_table.csv",
        "Based On (URL PIDs)",
        TEST_CASES_DIR / "all_identifiers.csv",
        "MBO Permanent Identifier*",
        separator="|",
        mbo_identifiers_only=True,
    )

    assert "mbo_url_form_not_in_catalogue" in invalid_values
    # ...while the same form pointing at a record which does exist passes.
    assert "mbo_dataset_one" not in invalid_values


def test_url_pids_check_is_opt_in():
    """Without the flag the column is checked verbatim, which is what the (mPID) columns need."""
    invalid_values = _get_invalid_list_column_values(
        TEST_CASES_DIR / "url_pids_child_table.csv",
        "Based On (URL PIDs)",
        TEST_CASES_DIR / "all_identifiers.csv",
        "MBO Permanent Identifier*",
        separator="|",
    )

    assert "https://example.com/someone-elses-dataset" in invalid_values


if __name__ == "__main__":
    pytest.main()
