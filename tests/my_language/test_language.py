import os
from pathlib import Path

from project.my_language.saver_to_dot import check_input, GraphTreeListener


def test_var():
    assert check_input('a = "text"')
    assert check_input("b = 532423")
    assert check_input("c = 43423")

    assert check_input("nodes = { 41, 3, 23 }")
    assert check_input('graph = load %"skos"')


def test_comments():
    assert check_input("test = 3 // la-la-la")
    assert check_input("// la-la-la\ntest = 3")
    assert check_input("test = 10\n//la-la-la")


def test_load():
    assert check_input('graph = load %"test"')
    assert check_input("graph = load path")


def test_graph_functions():
    assert check_input("graph = graph < starts custom_nodes")
    assert check_input("graph = graph - starts custom_nodes")
    assert check_input("graph = graph set finals custom_nodes")
    assert check_input("graph = graph + finals custom_nodes")

    assert check_input("finals = graph > finals")
    assert check_input("starts = graph get starts")
    assert check_input("reachables = graph > reachable")


def test_graph_operators():
    assert check_input("graph = first  &   second")
    assert check_input("graph = first  |   second")
    assert check_input("graph = first  ++  second")
    assert check_input("graph = first star")
    assert check_input("graph = first  ?   second")


def test_graph_functional():
    assert check_input(
        'modified_graph = graph <$> ((edg) -> { (edg > from, edg > to, "a") })'
    )
    assert check_input("predicate = [(fr, _, lb) -> { fr eq 10 }")
    assert check_input("nodes_equal_ten = (graph <?> predicate) > nodes")


def test_wrong_input():
    assert not check_input("graph = load")
    assert not check_input("graph")
    assert not check_input('graph = graph < start { "la-la-la" }')


def test_simple_examples():
    assert check_input(
        """graph = load %"skos" < starts {0, 1, 2, 3, 4, 5, 6, 7}
    reachables = graph > reachable"""
    )

    assert check_input(
        """q1 = a S b | a b
    q2 = a b
    print((graph & regex) > reachable)"""
    )

    assert check_input(
        """wine = load %"wine"
    pizza = load %"pizza"
    common_labels = (wine <?> (_, _, lb) -> { pizza ? lb }) get edges
    print(common_labels)"""
    )


def test_dot_graph():
    excepted_graph = """digraph language_graph {
1 [label=program];
1 -> 2;
2 [label=statement];
2 -> 3;
3 [label=pattern];
3 -> 4;
4 [label="Terminal: test"];
2 -> 5;
5 [label="Terminal:  "];
2 -> 6;
6 [label="Terminal: ="];
2 -> 7;
7 [label="Terminal:  "];
2 -> 8;
8 [label=expr];
8 -> 9;
9 [label=literal];
9 -> 10;
10 [label="Terminal: 1"];
1 -> 11;
11 [label="Terminal: <EOF>"];
}
"""

    path = Path("test.dot")
    GraphTreeListener("test = 1").save_in_dot(path)
    with open(path) as file:
        text = file.read()
    if os.path.exists(path):
        os.remove(path)

    assert text == excepted_graph
