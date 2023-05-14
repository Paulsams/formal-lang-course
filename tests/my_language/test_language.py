import os
from pathlib import Path

from project.my_language.my_language_interpteter import check_input, GraphTreeListener


def test_var():
    assert check_input('a = "text"')
    assert check_input("b = 532423")
    assert check_input("c = 43423;")

    assert check_input("Set<Node> nodes = { 41, 3, 23 }")
    assert check_input('Graph graph = load %"skos"')


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
    assert check_input("graph = fst  &   snd")
    assert check_input("graph = fst  |   snd")
    assert check_input("graph = fst  ++  snd")
    assert check_input("graph = fst star snd")
    assert check_input("graph = fst  ?   0")


def test_graph_functional():
    assert check_input(
        'modified_graph = graph <$> ([edg] -> { (edg > from, edg > to, "a") })'
    )
    assert check_input("predicate = [(fr, _, lb)] -> { fr eq 10 }")
    assert check_input("nodes_equal_ten = (graph <?> predicate) > nodes")


def test_wrong_input():
    assert not check_input("graph = load 1")
    assert not check_input('graph = load "test"')
    assert not check_input('graph = graph < start { "la-la-la" }')


def test_simple_examples():
    assert check_input(
        """graph = load %"skos" < starts {0, 1, 2, 3, 4, 5, 6, 7}
    reachables = graph > reachable"""
    )

    assert check_input(
        """Graph graph = CFG "S -> a S b | a b"
    Regex regex = Regex "a b"
    print((graph & regex) > reachable)"""
    )

    assert check_input(
        """wine = load %"wine"
    pizza = load %"pizza"
    common_labels = (wine <?> [(_, _, lb)] -> { pizza ? lb }) get edges
    print(common_labels)"""
    )


def test_dot_graph():
    excepted_graph = """digraph language_graph {
1 [label=program];
1 -> 2;
2 [label=statement];
2 -> 3;
3 [label=var];
3 -> 4;
4 [label=var_int];
4 -> 5;
5 [label="Terminal: test ="];
4 -> 6;
6 [label="Terminal:  "];
4 -> 7;
7 [label=int_expr];
7 -> 8;
8 [label="Terminal: 1"];
1 -> 9;
9 [label="Terminal: <EOF>"];
}
"""

    path = Path("test.dot")
    GraphTreeListener("test = 1").save_in_dot(path)
    with open(path) as file:
        text = file.read()
    if os.path.exists(path):
        os.remove(path)

    assert text == excepted_graph
