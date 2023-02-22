import pytest
from project import graph_utils
from networkx.drawing import nx_pydot


def setup_module(module):
    print(
        "graph_utils from create_labeled_graph_with_two_cycle_and_save_to_file setup module"
    )


def teardown_module(module):
    print(
        "graph_utils from create_labeled_graph_with_two_cycle_and_save_to_file teardown module"
    )


def test_ten():
    path_to_file = "test_ten.dot"

    print("create ten")
    graph_utils.create_labeled_graph_with_two_cycle_and_save_to_file(
        10, {"a", "b"}, path_to_file
    )
    assert nx_pydot.read_dot(path_to_file)


def test_two():
    path_to_file = "test_two.dot"

    print("create two")
    graph_utils.create_labeled_graph_with_two_cycle_and_save_to_file(
        2, {"c", "d"}, "test_two.dot"
    )
    assert nx_pydot.read_dot(path_to_file)
