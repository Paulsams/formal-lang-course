from pathlib import Path

from pyformlang.cfg import CFG
from networkx import MultiDiGraph
from typing import Set, Tuple

from project.cfg_utils import cfg_to_wcnf, cfg_str_to_wcnf, read_cfg


def cfg_str_by_hellings(
    graph: MultiDiGraph, cfg_text: str, start: str = "S"
) -> Set[Tuple]:
    """
    Translation text to CFG and execution of the Helling algorithm on it
    """
    return cfpg_by_hellings(graph, cfg_str_to_wcnf(cfg_text, start))


def read_cfg_and_hellings(
    graph: MultiDiGraph, path: Path, start: str = "S"
) -> Set[Tuple]:
    """
    Read CFG from given path and execution of the Helling algorithm on it
    """
    return cfpg_by_hellings(graph, read_cfg(path, start))


def cfpg_by_hellings(
    graph: MultiDiGraph,
    cfg: CFG,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> Set[Tuple]:
    """
    Calculation of Helling algorithm
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

    def executue_hellings():
        helling_result = set(tuple())
        wcnf = cfg_to_wcnf(cfg)
        eps_productions = set()
        term_productions = set()
        var_productions = set()

        for prod in wcnf.productions:
            if len(prod.body) == 1:
                term_productions.add(prod)
            elif len(prod.body) == 2:
                var_productions.add(prod)
            elif not prod.body:
                eps_productions.add(prod.head.value)

        helling_result = {
            (label, node, node) for node in graph.nodes for label in eps_productions
        } | {
            (term.head.value, v, u)
            for (v, u, label) in graph.edges(data="label")
            for term in term_productions
            if term.body[0].value == label
        }

        saved_result = helling_result.copy()
        while saved_result:
            popped_label, v1, u1 = saved_result.pop()
            r_changes = set()

            def check_vars(v, u, label1, label2):
                for triple in (
                    (p.head.value, v, u)
                    for p in var_productions
                    if (p.head.value, v, u) not in helling_result
                    and p.body[0].value == label1
                    and p.body[1].value == label2
                ):
                    saved_result.add(triple)
                    r_changes.add(triple)

            for (label, v2, _) in (t for t in helling_result if t[2] == v1):
                check_vars(v2, u1, label, popped_label)
            for (label, _, u2) in (t for t in helling_result if t[1] == u1):
                check_vars(v1, u2, popped_label, label)

            helling_result |= r_changes
        return helling_result

    result = {
        (x, y)
        for (label, x, y) in executue_hellings()
        if x in start_nodes and y in final_nodes and label == start_symbol
    }
    return result
