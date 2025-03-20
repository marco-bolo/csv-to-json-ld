from pathlib import Path

import rdflib
from rdflib.compare import graph_diff


def _get_test_cases_dir() -> Path:
    return Path(".").rglob("testcases").__next__()


TEST_CASES_DIR = _get_test_cases_dir()


def assert_file_contains_only_these_triples(
    actual_triples_file: Path, expected_ttl: str
) -> None:
    expected_graph = rdflib.Graph()
    expected_graph.parse(data=expected_ttl, format="ttl")
    actual_graph: rdflib.Graph = rdflib.Graph()
    actual_graph.parse(actual_triples_file)
    (_, in_first, in_second) = graph_diff(expected_graph, actual_graph)
    assert not any(in_first), list(in_first)
    assert not any(in_second), list(in_second)

def assert_file_contains_these_triples(
    actual_triples_file: Path, prefixes: str, expected_ttl: str
) -> None:
    actual_graph: rdflib.Graph = rdflib.Graph()
    actual_graph.parse(actual_triples_file)

    results = list(actual_graph.query(f"""
        {prefixes}
        
        ASK 
        WHERE {{
            {expected_ttl}
        }}
    """))

    assert len(results) == 1
    assert isinstance(results[0], bool)
    assert results[0] is True