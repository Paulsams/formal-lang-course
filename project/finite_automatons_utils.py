from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    NondeterministicFiniteAutomaton,
    DeterministicFiniteAutomaton,
)
from networkx import MultiDiGraph


def build_dfa_from_regex(expr: str) -> DeterministicFiniteAutomaton:
    return Regex(expr).to_epsilon_nfa().to_deterministic().minimize()


def build_from_networkx_graph(
    graph: MultiDiGraph, start_nodes: [] = None, end_nodes: [] = None
) -> NondeterministicFiniteAutomaton:
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
