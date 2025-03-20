from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from mbocsvwscripts.partition import (
    _partition_to_individual_files,
    _list_partition_files_out,
)
from .utils import TEST_CASES_DIR, assert_file_contains_only_these_triples


def test_expected_partitions_listed():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        partitioned_files = _list_partition_files_out(
            TEST_CASES_DIR / "bulk-licenses.ttl", tmp_dir
        )

        assert partitioned_files == {
            tmp_dir / "mbo_TODO_LICENSE_1-data.json",
            tmp_dir / "mbo_TODO_LICENSE_1.json",
            tmp_dir / "mbo_TODO_LICENSE_2-data.json",
            tmp_dir / "mbo_TODO_LICENSE_2.json",
            tmp_dir / "mbo_TODO_LICENSE_3-data.json",
            tmp_dir / "mbo_TODO_LICENSE_3.json",
            tmp_dir / "mbo_TODO_LICENSE_4-data.json",
            tmp_dir / "mbo_TODO_LICENSE_4.json",
        }


def test_expected_partitions_listed_hash():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        partitioned_files = _list_partition_files_out(
            TEST_CASES_DIR / "bulk-monetary-grant.ttl", tmp_dir
        )

        assert partitioned_files == {tmp_dir / "mbo_todo_monetary_grant_1.json"}


def test_partitions_contain_expected_triples():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        _partition_to_individual_files(TEST_CASES_DIR / "bulk-licenses.ttl", tmp_dir)

        assert_file_contains_only_these_triples(
            tmp_dir / "mbo_TODO_LICENSE_1.json",
            """
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix schema: <https://schema.org/>.
            
            mbo:mbo_TODO_LICENSE_1 a schema:CreativeWork;
              schema:name "Creative Commons Zero v1.0 Universal";
              schema:url <https://spdx.org/licenses/CC0-1.0> .
        """,
        )

        assert_file_contains_only_these_triples(
            tmp_dir / "mbo_TODO_LICENSE_1-data.json",
            """
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix schema: <https://schema.org/>.

            mbo:mbo_TODO_LICENSE_1-data a schema:DataDownload;
                                       schema:creator mbo:mbo_todo_organization_mbo;
                                       schema:about mbo:mbo_TODO_LICENSE_1;
                                       schema:contentUrl <file:/work/license.csv#row=1>.
        """,
        )

        assert_file_contains_only_these_triples(
            tmp_dir / "mbo_TODO_LICENSE_2.json",
            """
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix schema: <https://schema.org/>.

            mbo:mbo_TODO_LICENSE_2 a schema:CreativeWork;
              schema:name "European Union Public License 1.0";
              schema:url <https://spdx.org/licenses/EUPL-1.0>;
              schema:description "The European Commission has approved the EUPL on 9 January 2007.".
        """,
        )

        assert_file_contains_only_these_triples(
            tmp_dir / "mbo_TODO_LICENSE_2-data.json",
            """
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix schema: <https://schema.org/>.

            mbo:mbo_TODO_LICENSE_2-data a schema:DataDownload;
                                       schema:creator mbo:mbo_todo_organization_mbo;
                                       schema:about mbo:mbo_TODO_LICENSE_2;
                                       schema:contentUrl <file:/work/license.csv#row=2>.
        """,
        )

        assert_file_contains_only_these_triples(
            tmp_dir / "mbo_TODO_LICENSE_3.json",
            """
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix schema: <https://schema.org/>.

            mbo:mbo_TODO_LICENSE_3 a schema:CreativeWork;
              schema:name "European Union Public License 1.1";
              schema:url <https://spdx.org/licenses/EUPL-1.1>;
              schema:description "This license was released: 16 May 2008. This license is available in the 22 official languages of the EU.".
        """,
        )

        assert_file_contains_only_these_triples(
            tmp_dir / "mbo_TODO_LICENSE_3-data.json",
            """
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix schema: <https://schema.org/>.

            mbo:mbo_TODO_LICENSE_3-data a schema:DataDownload;
                                       schema:creator mbo:mbo_todo_organization_mbo;
                                       schema:about mbo:mbo_TODO_LICENSE_3;
                                       schema:contentUrl <file:/work/license.csv#row=3>.
        """,
        )

        assert_file_contains_only_these_triples(
            tmp_dir / "mbo_TODO_LICENSE_4.json",
            """
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix schema: <https://schema.org/>.

            mbo:mbo_TODO_LICENSE_4 a schema:CreativeWork;
              schema:name "European Union Public License 1.2";
              schema:url <https://spdx.org/licenses/EUPL-1.2>;
              schema:description "This license was released: 19 May 2016. This license is available in the 22 official languages of the EU.".
        """,
        )

        assert_file_contains_only_these_triples(
            tmp_dir / "mbo_TODO_LICENSE_4-data.json",
            """
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix schema: <https://schema.org/>.

            mbo:mbo_TODO_LICENSE_4-data a schema:DataDownload;
                                       schema:creator mbo:mbo_todo_organization_mbo;
                                       schema:about mbo:mbo_TODO_LICENSE_4;
                                       schema:contentUrl <file:/work/license.csv#row=4>.
        """,
        )


def test_partitions_contains_expected_hash_urls():
    """
    Make sure that has URLs are stuck into the same file as the parent URL since they'll resolvable to the same file.
    """
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        _partition_to_individual_files(
            TEST_CASES_DIR / "bulk-monetary-grant.ttl", tmp_dir
        )

        assert_file_contains_only_these_triples(
            tmp_dir / "mbo_todo_monetary_grant_1.json",
            """
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix schema: <https://schema.org/>.

            mbo:mbo_todo_monetary_grant_1 a schema:MonetaryGrant;
              schema:sdPublisher mbo:mbo_todo_person_roblinksdata;
              schema:name "Some grant";
              schema:amount <https://w3id.org/marco-bolo/mbo_todo_monetary_grant_1#amount> .
            
            <https://w3id.org/marco-bolo/mbo_todo_monetary_grant_1#amount> a schema:MonetaryAmount;
              schema:value "1";
              schema:currency "Kudos" .
        """,
        )


if __name__ == "__main__":
    pytest.main()
