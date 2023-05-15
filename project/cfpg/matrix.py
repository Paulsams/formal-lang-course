from pathlib import Path
from typing import Set, Tuple

from pyformlang.cfg import CFG
from networkx import MultiDiGraph
from scipy.sparse import dok_matrix

from project.cfg_utils import cfg_to_wcnf, cfg_str_to_wcnf, read_cfg


def cfg_str_transitive_closure(
    graph: MultiDiGraph, cfg_text: str, start: str = "S"
) -> Set[Tuple]:
    """
    Translation text to CFG and execution of the Matrix algorithm on it
    """
    return cfpg_transitive_closure(graph, cfg_str_to_wcnf(cfg_text, start))


def read_cfg_and_transitive_closure(
    graph: MultiDiGraph, path: Path, start: str = "S"
) -> Set[Tuple]:
    """
    Read CFG from given path and execution of the Matrix algorithm on it
    """
    return cfpg_transitive_closure(graph, read_cfg(path, start))


def cfpg_transitive_closure(
    graph: MultiDiGraph,
    cfg: CFG,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> Set[Tuple]:
    """
    Calculation of Matrix algorithm
    :param graph: this graph needed for algorithm
    :param cfg: this cfg needed for algorithm
    :param start_nodes: if list is None, then nodes from the graph will be taken
    :param final_nodes: if list is None, then nodes from the graph will be taken
    :return:
    """
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes
    start_symbol = cfg.start_symbol.value

    def execute():
        count = graph.number_of_nodes()

        wcnf = cfg_to_wcnf(cfg)
        eps_productions = set()
        term_productions = set()
        var_productions = set()

        for prod in wcnf.productions:
            if len(prod.body) == 1:
                term_productions.add(prod)
            elif len(prod.body) == 2:
                var_productions.add((prod.head, prod.body[0], prod.body[1]))
            elif not prod.body:
                eps_productions.add(prod.head.value)

        matrices = {
            non_terminal.value: dok_matrix((count, count), dtype=bool)
            for non_terminal in wcnf.variables
        }

        for i, j, label in graph.edges(data="label"):
            for non_terminal in (
                tp.head.value for tp in term_productions if tp.body[0].value == label
            ):
                matrices[non_terminal][i, j] = True

        for i in range(count):
            for non_terminal in eps_productions:
                matrices[non_terminal][i, i] = True

        changed = True
        while changed:
            changed = False
            for h, b1, b2 in var_productions:
                nnz_old = matrices[h].nnz
                matrices[h] += matrices[b1] @ matrices[b2]
                changed |= matrices[h].nnz != nnz_old

        return {
            (non_terminal, i, j)
            for non_terminal, matrix in matrices.items()
            for i, j in zip(*matrix.nonzero())
        }

    result = {
        (x, y)
        for (label, x, y) in execute()
        if x in start_nodes and y in final_nodes and label == start_symbol
    }
    return result
