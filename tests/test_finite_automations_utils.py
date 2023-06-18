import pytest
from project import graph_utils
from project import finite_automatons_utils
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, EpsilonNFA


def setup_module(module):
    print("finite_automatons_utils from get_graph_info setup module")


def teardown_module(module):
    print("finite_automatons_utils from get_graph_info teardown module")


def test_build_graph_dfa_from_complex_check_requirements():
    print("build dfa from regex and check requirements")

    regex = "xy* (x | y*)"
    dfa = finite_automatons_utils.build_dfa_from_regex(regex)

    excepted = NondeterministicFiniteAutomaton()
    excepted.add_start_state(0)
    excepted.add_final_state(0)
    excepted.add_final_state(1)
    excepted.add_final_state(2)
    excepted.add_transitions([(0, "xy", 0), (0, "y", 1), (1, "y", 1), (0, "x", 2)])

    assert excepted.is_equivalent_to(dfa)


def test_build_graph_dfa_from_simple_regex():
    print("build dfa from simple regex")
    regex = "xy* (x | y*) | ab (x | y*) | (x | a*) (x | y*)"
    dfa = finite_automatons_utils.build_dfa_from_regex(regex)
    assert dfa.is_deterministic()
    dfa_min = dfa.minimize()
    assert dfa.is_equivalent_to(dfa_min)


def test_build_from_networkx_graph():
    first_size = 3
    second_size = 2

    print("build dfa from networkx graph")

    graph = graph_utils.create_labeled_graph_with_two_cycle(
        first_size, second_size, labels=("a", "b")
    )
    nfa = finite_automatons_utils.build_enfa_from_networkx_graph(graph, [0], [3])

    expected = NondeterministicFiniteAutomaton(range(first_size * second_size))
    expected.add_start_state(0)
    expected.add_final_state(3)

    for i in range(0, first_size + 1):
        expected.add_transition(i, "a", (i + 1) % (first_size + 1))
    for i in range(first_size + 1, first_size + second_size + 1):
        expected.add_transition(i, "b", (i + 1) % (first_size + second_size + 1))
    expected.add_transition(0, "b", first_size + 1)

    assert expected.is_equivalent_to(nfa)


def test_build_from_loaded_graph():
    print("build dfa from loaded graph")

    graph = graph_utils.load_graph("wc")
    nfa = finite_automatons_utils.build_enfa_from_networkx_graph(graph)

    exceptedGraphInfo = graph_utils.GraphInfo(
        count_vertices=332, count_edges=269, labels=["d", "a"]
    )

    assert len(nfa.states) == exceptedGraphInfo.count_vertices
    assert len(nfa.final_states) == exceptedGraphInfo.count_vertices
    assert len(nfa.start_states) == exceptedGraphInfo.count_vertices


def test_intersect_two_automata():
    nfa1 = EpsilonNFA()
    nfa1.add_start_state(0)
    nfa1.add_final_state(0)
    nfa1.add_transitions([(0, "a", 1), (0, "b", 1), (1, "b", 0)])

    nfa2 = EpsilonNFA()
    nfa2.add_start_state(0)
    nfa2.add_final_state(2)
    nfa2.add_transitions([(0, "a", 1), (1, "b", 2), (2, "b", 0), (0, "b", 2)])

    actual = finite_automatons_utils.intersection_automations(nfa1, nfa2)

    expected = EpsilonNFA()
    expected.add_start_state(0)
    expected.add_final_state(2)
    expected.add_transitions(
        [
            (0, "b", 5),
            (1, "b", 5),
            (2, "b", 3),
            (3, "b", 2),
            (4, "b", 2),
            (5, "b", 0),
            (0, "a", 4),
        ]
    )
    assert expected.is_equivalent_to(actual)


def test_fdf():
    regex = "(a | b)*"
    graph = graph_utils.create_labeled_graph_with_two_cycle(1, 2, labels=("a", "b"))

    got = finite_automatons_utils.rpq(regex, graph, [0, 2], [2, 1])
    assert {(0, 1), (0, 2), (2, 1), (2, 2)} == got

    got = finite_automatons_utils.rpq(regex, graph, [1], [0])
    assert {(1, 0)} == got


def test_rpq_with_separated():
    graph = graph_utils.create_labeled_graph_with_two_cycle(3, 3, ("a", "b"))
    regex = "(a*|b)"
    result = finite_automatons_utils.bfs_based_rpq_from_graph_and_regex(
        graph, regex, True
    )

    expected = {
        0: [0, 1, 2, 3, 4],
        1: [0, 1, 2, 3],
        2: [0, 1, 2, 3],
        3: [0, 1, 2, 3],
        4: [5],
        5: [6],
        6: [0],
    }

    assert result == expected


def test_rpq_without_separated():
    graph = graph_utils.create_labeled_graph_with_two_cycle(3, 3, labels=("a", "b"))
    regex = "(a*|b)"
    first = finite_automatons_utils.build_enfa_from_networkx_graph(graph, None, None)
    second = finite_automatons_utils.build_dfa_from_regex(regex)
    result = finite_automatons_utils.bfs_based_rpq(first, second, False)

    expected = {0, 1, 2, 3, 4, 5, 6}
    assert result == expected
