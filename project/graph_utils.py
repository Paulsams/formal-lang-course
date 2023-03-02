import cfpq_data
from networkx.drawing import nx_pydot
from networkx import MultiDiGraph
from typing import List, NamedTuple, Tuple


class GraphInfo(NamedTuple):
    count_vertices: int
    count_edges: int
    labels: List[str]


def get_graph_info(name: str) -> GraphInfo:
    """Returns tuple of the form: (number of vertices, number of edges, List[str] - labels)"""
    graph = load_graph(name)
    return GraphInfo(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        cfpq_data.get_sorted_labels(graph),
    )


def create_labeled_graph_with_two_cycle_and_save_to_file(
    count_nodes_in_first_cycle: int,
    count_nodes_in_second_cycle: int,
    labels: Tuple[str, str],
    path_file: str,
) -> None:
    graph = create_labeled_graph_with_two_cycle(
        count_nodes_in_first_cycle, count_nodes_in_second_cycle, labels
    )
    save_graph_to_file(graph, path_file)


def save_graph_to_file(graph: MultiDiGraph, path_file: str) -> None:
    nx_graph = nx_pydot.to_pydot(graph)
    nx_graph.write(path_file)


def create_labeled_graph_with_two_cycle(
    count_nodes_in_first_cycle: int,
    count_nodes_in_second_cycle: int,
    labels: Tuple[str, str],
) -> MultiDiGraph:
    return cfpq_data.labeled_two_cycles_graph(
        n=count_nodes_in_first_cycle, m=count_nodes_in_second_cycle, labels=labels
    )


def load_graph_from_file(path_file: str) -> MultiDiGraph:
    graph = nx_pydot.read_dot(path_file)
    # graph.remove_node('\n')
    return graph


def load_graph(name: str) -> MultiDiGraph:
    graph_path = cfpq_data.download(name)
    return cfpq_data.graph_from_csv(graph_path)
