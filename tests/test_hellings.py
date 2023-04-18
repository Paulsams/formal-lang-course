import pytest
from pyformlang.cfg import Variable, CFG
import cfpq_data

from project.helling import cfpg_by_hellings


def test_hellings():
    def local(cfg_text, expected_edges):
        graph = cfpq_data.labeled_two_cycles_graph(2, 1, labels=("a", "b"))
        cfg = CFG.from_text(cfg_text, Variable("S"))

        assert cfpg_by_hellings(graph, cfg) == expected_edges

    local("S -> a b", {(2, 3)})
    local(
        "S -> a S b S | $",
        {(0, 0), (1, 1), (0, 3), (2, 0), (2, 3), (3, 3), (2, 2), (1, 0), (1, 3)},
    )
    local(
        "S -> a S | P\nP -> b P | b",
        {(0, 0), (0, 3), (2, 0), (3, 0), (2, 3), (3, 3), (1, 0), (1, 3)},
    )
    local(
        "S -> a S | P\nP -> b P | $",
        {
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 0),
            (1, 1),
            (1, 2),
            (1, 3),
            (2, 0),
            (2, 1),
            (2, 2),
            (2, 3),
            (3, 0),
            (3, 3),
        },
    )
