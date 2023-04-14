from typing import Tuple, Dict, Any
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    NondeterministicFiniteAutomaton,
    DeterministicFiniteAutomaton,
    EpsilonNFA,
)
import scipy.sparse as sp
from networkx import MultiDiGraph
from scipy.sparse import (
    dok_matrix,
    block_diag,
    dok_array,
    vstack,
)


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


def intersection_automations(first: EpsilonNFA, second: EpsilonNFA) -> EpsilonNFA:
    """returns the intersection of two finite automata"""
    (first_indexed_states, first_matrix) = get_states_and_matrix_from_nfa(first)
    (second_indexed_states, second_matrix) = get_states_and_matrix_from_nfa(second)

    labels = first_matrix.keys() & second_matrix.keys()

    indexed_states = dict()
    start_states = set()
    final_states = set()
    matrix = dict()

    for label in labels:
        matrix[label] = sp.kron(first_matrix[label], second_matrix[label], format="dok")

    for first_state, first_index in first_indexed_states.items():
        for second_state, second_index in second_indexed_states.items():
            new_state_index = first_index * len(second.states) + second_index
            indexed_states[new_state_index] = new_state_index

            if (
                first_state in first.start_states
                and second_state in second.start_states
            ):
                start_states.add(new_state_index)

            if (
                first_state in first.final_states
                and second_state in second.final_states
            ):
                final_states.add(new_state_index)

    return build_nfa(matrix, indexed_states, start_states, final_states)


def build_nfa(
    matrix, indexed_states, start_states, final_states
) -> NondeterministicFiniteAutomaton:
    """Builds a finite automaton based on a boolean matrix, indexed states, start and final states."""
    nfa = NondeterministicFiniteAutomaton()

    for label in matrix.keys():
        arr = matrix[label].toarray()
        for i in range(len(arr)):
            for j in range(len(arr)):
                if arr[i][j]:
                    nfa.add_transition(indexed_states[i], label, indexed_states[j])

    for start_state in start_states:
        nfa.add_start_state(indexed_states[start_state])
    for final_state in final_states:
        nfa.add_final_state(indexed_states[final_state])

    return nfa


def get_states_and_matrix_from_nfa(nfa: EpsilonNFA) -> (Dict, Dict[Any, dok_matrix]):
    """Returns indexed states and a Boolean matrix by a finite automaton."""
    indexed_states = {state: index for (index, state) in enumerate(nfa.states)}
    count_states = len(nfa.states)

    matrix = dict()
    for initial_state, labels_and_states in nfa.to_dict().items():
        for label, states in labels_and_states.items():
            if not isinstance(states, set):
                states = {states}
            for target_state in states:
                if label not in matrix:
                    matrix[label] = dok_matrix((count_states, count_states), dtype=bool)

                matrix[label][
                    indexed_states[initial_state], indexed_states[target_state]
                ] = True

    return (indexed_states, matrix)


def transitive_closure(matrix) -> dok_matrix:
    """Returns the transitive closure matrix by boolean matrix."""
    if not matrix.values():
        return dok_matrix((1, 1))

    closure = sum(matrix.values())
    prev = closure.nnz
    current = 0

    while prev != current:
        closure += closure @ closure
        prev, current = current, closure.nnz

    return closure


def rpq(
    regex: str, graph: MultiDiGraph, start_states: [] = None, final_states: [] = None
) -> [Tuple[any, any]]:
    """
    Returns result from Regular Pass Query.
    :param regex: regular expression by which the path is searched
    :param graph: graph by which the comparison takes place
    :param start_states: if the list is empty, then it is assumed that all vertices are starting.
    :param final_states: if the list is empty, then it is assumed that all vertices are starting.
    :return: pairs of vertices connected by forming a word from the language.
    """
    first = build_nfa_from_networkx_graph(graph, start_states, final_states)
    second = build_dfa_from_regex(regex)

    intersection = intersection_automations(first, second)
    (_, matrix) = get_states_and_matrix_from_nfa(intersection)

    closure = transitive_closure(matrix)
    rows, columns = closure.nonzero()
    result = set()
    for start, fin in zip(rows, columns):
        if start in intersection.start_states and fin in intersection.final_states:
            result.add((start // len(second.states), fin // len(second.states)))
    return result


def bfs_based_rpq_from_graph_and_regex(
    graph: MultiDiGraph,
    regex: str,
    separately: bool,
    start_nodes: [] = None,
    end_nodes: [] = None,
):
    """
    Reachability check function with regular constraints.
    :param graph: graph on which the automaton is built. Must have a "label" field on the edges.
    :param regex: regular expression by which second graph is constructed
    :param separately: is separated output
    :param end_nodes: if the list is empty, then it is assumed that all vertices are starting.
    :param start_nodes: if the list is empty, then it is assumed that all vertices are starting.
    :return: set of available vertices
    """
    return bfs_based_rpq(
        build_nfa_from_networkx_graph(graph, start_nodes, end_nodes),
        build_dfa_from_regex(regex),
        separately,
    )


def bfs_based_rpq(
    first: NondeterministicFiniteAutomaton,
    second: NondeterministicFiniteAutomaton,
    separately: bool,
):
    """
    Reachability check function with regular constraints.
    :param first: first graph
    :param second: second graph
    :param separately: is separated output
    :return: set of available vertices
    """
    (first_indexed_states, first_matrix) = get_states_and_matrix_from_nfa(first)
    (second_indexed_states, second_matrix) = get_states_and_matrix_from_nfa(second)
    first_start_state_indexes = {node.value for node in first.start_states}
    first_final_state_indexes = {node.value for node in first.final_states}
    second_start_state_indexes = {node.value for node in second.start_states}
    second_final_state_indexes = {node.value for node in second.final_states}
    first_n = len(first.states)
    second_n = len(second.states)

    def transform_rows(front_part: dok_array):
        front_part_out = dok_array(front_part.shape, dtype=bool)
        xi, yj = front_part.nonzero()
        for i, j in zip(xi, yj):
            if j < second_n:
                row_second_part = front_part[[i], second_n:]
                if row_second_part.nnz > 0:
                    shift = i - i % second_n
                    front_part_out[shift + j, j] = True
                    front_part_out[[shift + j], second_n:] += row_second_part
        return front_part_out

    def get_front(start_states=None):
        front_out = dok_matrix((second_n, first_n + second_n), dtype=bool)

        front_first = dok_matrix((1, first_n), dtype=bool)
        for i in start_states:
            front_first[0, i] = True
        for ss in second_start_state_indexes:
            i = second_indexed_states[ss]
            front_out[i, i] = True
            front_out[[i], second_n:] = front_first
        return front_out

    direct_sum = {
        label: block_diag((second_matrix[label], first_matrix[label]))
        for label in (first_matrix.keys() & second_matrix.keys())
    }

    front = (
        vstack([get_front({i}) for i in first_start_state_indexes])
        if separately
        else get_front(first_start_state_indexes)
    )

    def update_visited(vst, func):
        vst_nnz = vst.nnz
        for _, matrix in direct_sum.items():
            front_part = func(matrix)
            vst += transform_rows(front_part)
        return vst, vst_nnz != vst.nnz

    visited = dok_array(front.shape, dtype=bool)
    (visited, check) = update_visited(visited, lambda m: front @ m)
    if check:
        while check:
            (visited, check) = update_visited(visited, lambda m: visited @ m)

    answer = set()
    second_states = list(second_indexed_states.keys())
    first_states = list(first_indexed_states.keys())
    rows, columns = visited.nonzero()
    for i, j in zip(rows, columns):
        if j >= second_n and second_states[i % second_n] in second_final_state_indexes:
            state_index = j - second_n
            if first_states[state_index] in first_final_state_indexes:
                answer.add((i // second_n, state_index) if separately else state_index)

    copy = answer
    if separately:
        answer = {}
        for i in copy:
            answer.setdefault(i[0], []).append(i[1])
        for key, value in answer.items():
            answer[key] = sorted(value)
    return answer
