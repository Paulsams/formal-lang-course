import pytest
import os
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


def test_five_and_ten():
    path_to_file = "test_five_and_ten.dot"

    print("create ten")
    graph_utils.create_labeled_graph_with_two_cycle_and_save_to_file(
        5, 10, ("a", "b"), path_to_file
    )
    graph = nx_pydot.read_dot(path_to_file)
    os.remove(path_to_file)
    exceptedGraph = nx_pydot.read_dot(
        "tests/test_create_two_cycle_labeled_graph/excepted_five_and_ten.dot"
    )

    assert graph.graph == exceptedGraph.graph


def test_three_and_two():
    path_to_file = "test_three_and_two.dot"

    print("create two")
    graph_utils.create_labeled_graph_with_two_cycle_and_save_to_file(
        3, 2, ("c", "d"), path_to_file
    )
    graph = nx_pydot.read_dot(path_to_file)
    os.remove(path_to_file)
    exceptedGraph = nx_pydot.read_dot(
        "tests/test_create_two_cycle_labeled_graph/excepted_three_and_two.dot"
    )

    assert graph.graph == exceptedGraph.graph
