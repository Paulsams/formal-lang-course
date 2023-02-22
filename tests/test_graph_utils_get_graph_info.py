import pytest
from project import graph_utils


def setup_module(module):
    print("graph_utils from get_graph_info setup module")


def teardown_module(module):
    print("graph_utils from get_graph_info teardown module")


def test_get_graph_info_skos():
    print("load skos graph info")
    assert graph_utils.get_graph_info("skos")


def test_get_graph_info_bzip():
    print("load bzip graph info")
    assert graph_utils.get_graph_info("bzip")
