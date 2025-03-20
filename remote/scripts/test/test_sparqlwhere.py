import pytest

from mbocsvwscripts.sparqlwhere import _find_files_matching_sparql_query
from .utils import TEST_CASES_DIR

_TTL_DIR_CONTAINING_LICENSES = TEST_CASES_DIR / "ttl-containing-licenses"
_JSONLD_DIR_CONTAINING_DATASETS = TEST_CASES_DIR / "jsonld-containing-datasets"


def test_sparql_query_ask_ttl_multiple_results():
    matching_files = set(
        _find_files_matching_sparql_query(
            _TTL_DIR_CONTAINING_LICENSES,
            "*.ttl",
            """
        ASK
        WHERE {
            [] a <https://schema.org/CreativeWork>.
        }
    """,
        )
    )

    assert matching_files == {
        _TTL_DIR_CONTAINING_LICENSES / "mbo_TODO_LICENSE_1.ttl",
        _TTL_DIR_CONTAINING_LICENSES / "mbo_TODO_LICENSE_2.ttl",
        _TTL_DIR_CONTAINING_LICENSES / "mbo_TODO_LICENSE_3.ttl",
        _TTL_DIR_CONTAINING_LICENSES / "mbo_TODO_LICENSE_4.ttl",
    }
    # N.B. This implicitly asserts that the `*-input-metadata.ttl` files aren't in the results set which is important.


def test_sparql_query_ask_jsonld_no_results():
    matching_files = set(
        _find_files_matching_sparql_query(
            _JSONLD_DIR_CONTAINING_DATASETS,
            "*.json",
            """
        ASK
        WHERE {
            [] a <https://schema.org/DigitalDocument>.
        }
    """,
        )
    )

    assert not any(matching_files)


def test_sparql_query_select_jsonld_multiple_results():
    matching_files = set(
        _find_files_matching_sparql_query(
            _JSONLD_DIR_CONTAINING_DATASETS,
            "*.json",
            """
        SELECT ?dataset
        WHERE {
            ?dataset a <https://schema.org/Dataset>.
        }
    """,
        )
    )

    assert matching_files == {
        _JSONLD_DIR_CONTAINING_DATASETS / "mbo_TODO_DATASET_2.json",
        _JSONLD_DIR_CONTAINING_DATASETS / "mbo_TODO_DATASET_5.json",
        _JSONLD_DIR_CONTAINING_DATASETS / "mbo_TODO_DATASET_6.json",
        _JSONLD_DIR_CONTAINING_DATASETS / "mbo_TODO_DATASET_10.json",
    }


def test_sparql_query_select_ttl_no_results():
    matching_files = set(
        _find_files_matching_sparql_query(
            _TTL_DIR_CONTAINING_LICENSES,
            "*.ttl",
            """
        SELECT ?s
        WHERE {
            ?s a <https://schema.org/DigitalDocument>.
        }
    """,
        )
    )

    assert not any(matching_files)


if __name__ == "__main__":
    pytest.main()
