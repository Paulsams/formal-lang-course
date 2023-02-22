import cfpq_data
from networkx.drawing import nx_pydot
from networkx import MultiDiGraph
from typing import Tuple


def get_graph_info(name: str) -> Tuple[int, int, list]:
    """Returns tuple of the form: (number of vertices, number of edges, List[str] - labels)"""
    graph = load_graph(name)
    return (
        graph.number_of_nodes(),
        graph.number_of_edges(),
        cfpq_data.get_sorted_labels(graph),
    )


def create_labeled_graph_with_two_cycle_and_save_to_file(
    count_nodes_in_cycle: int, labels, path_file: str
) -> None:
    graph = cfpq_data.labeled_two_cycles_graph(count_nodes_in_cycle, labels)
    save_graph_to_file(graph, path_file)


def save_graph_to_file(graph: MultiDiGraph, path_file: str) -> None:
    nx_graph = nx_pydot.to_pydot(graph)
    nx_graph.write(path_file)


def load_graph(name: str) -> MultiDiGraph:
    graph_path = cfpq_data.download(name)
    return cfpq_data.graph_from_csv(graph_path)
