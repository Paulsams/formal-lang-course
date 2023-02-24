import pytest
from project import graph_utils


def setup_module(module):
    print("graph_utils from get_graph_info setup module")


def teardown_module(module):
    print("graph_utils from get_graph_info teardown module")


def test_get_graph_info_wc():
    print("load skos graph info")
    exceptedGraphInfo = graph_utils.GraphInfo(
        count_vertices=332, count_edges=269, labels=["d", "a"]
    )
    assert graph_utils.get_graph_info("wc") == exceptedGraphInfo


def test_get_graph_info_bzip():
    print("load bzip graph info")
    exceptedGraphInfo = graph_utils.GraphInfo(
        count_vertices=632, count_edges=556, labels=["d", "a"]
    )
    assert graph_utils.get_graph_info("bzip") == exceptedGraphInfo
