import pytest
from pyformlang.cfg import Variable
from pyformlang.regular_expression import Regex

from project.ecfg import ECFG
from project.rsm import rsm_from_ecfg, minimize_rsm


def test_create_rsm_from_ecfg():
    expected_ecfg_prod = {Variable("S"): Regex("(((x.(S.(y.S)))|$)|(a.(S.(b.S))))")}

    expected_ecfg = ECFG(expected_ecfg_prod.keys(), expected_ecfg_prod, Variable("S"))
    rsm = rsm_from_ecfg(expected_ecfg)
    assert rsm.start_symbol == expected_ecfg.start_symbol
    assert all(
        rsm.boxes[v] == expected_ecfg.productions[v].to_epsilon_nfa()
        for v in expected_ecfg.productions.keys()
    )


def test_minimize():
    expected_ecfg_prod = {
        Variable("P"): Regex("((Q|(b.P))|$)"),
        Variable("S"): Regex("(($|(a.S))|P)"),
        Variable("Q"): Regex("((c.Q)|$)"),
    }

    expected_ecfg = ECFG(expected_ecfg_prod.keys(), expected_ecfg_prod, Variable("S"))
    rsm = minimize_rsm(rsm_from_ecfg(expected_ecfg))
    assert rsm.start_symbol == expected_ecfg.start_symbol
    assert all(
        rsm.boxes[v] == expected_ecfg.productions[v].to_epsilon_nfa().minimize()
        for v in expected_ecfg.productions.keys()
    )
