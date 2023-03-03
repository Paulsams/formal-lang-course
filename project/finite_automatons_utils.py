from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    NondeterministicFiniteAutomaton,
    DeterministicFiniteAutomaton,
)
from networkx import MultiDiGraph


def build_dfa_from_regex(expr: str) -> DeterministicFiniteAutomaton:
    """Builds a graph based on the passed regular expression"""
    return Regex(expr).to_epsilon_nfa().minimize()


def build_nfa_from_networkx_graph(
    graph: MultiDiGraph, start_nodes: [] = None, end_nodes: [] = None
) -> NondeterministicFiniteAutomaton:
    """
    The function builds a Nondeterministic Finite Automaton using data from a MultiDiGraph

    Args:
        graph: graph on which the automaton is built. Must have a "label" field on the edges.
        start_nodes: if the list is empty, then it is assumed that all vertices are starting.
        end_nodes: if the list is empty, then it is assumed that all vertices are starting.
    """
    nfa = NondeterministicFiniteAutomaton(graph)

    if start_nodes is None:
        start_nodes = graph.nodes
    if end_nodes is None:
        end_nodes = graph.nodes

    for node in start_nodes:
        nfa.add_start_state(node)

    for node in end_nodes:
        nfa.add_final_state(node)

    for v, u, data in graph.edges(data=True):
        nfa.add_transition(v, data["label"], u)

    return nfa
