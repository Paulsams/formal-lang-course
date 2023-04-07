import pytest
from pathlib import Path
from pyformlang.cfg import Variable, CFG
from pyformlang.regular_expression import Regex

from project.ecfg import ECFG, ecfg_from_cfg, ecfg_from_text, ecfg_from_file


def compare_ecfg(actual_ecfg: ECFG, expected_ecfg: ECFG):
    assert actual_ecfg.start_symbol == expected_ecfg.start_symbol
    assert actual_ecfg.variables == expected_ecfg.variables
    assert all(
        actual_ecfg.productions[key].to_epsilon_nfa()
        == expected_ecfg.productions[key].to_epsilon_nfa()
        for key in expected_ecfg.productions
    )


def test_create_ecfg_from_cfg():
    cfg_text = """S -> a S b S | x S y S | $"""
    expected_ecfg_prod = {Variable("S"): Regex("(((x.(S.(y.S)))|$)|(a.(S.(b.S))))")}

    cfg = CFG.from_text(cfg_text)
    expected_ecfg = ECFG(expected_ecfg_prod.keys(), expected_ecfg_prod)
    actual_ecfg = ecfg_from_cfg(cfg)
    compare_ecfg(actual_ecfg, expected_ecfg)


def test_from_text():
    cfg_text = """S -> a S | $ | P
               P -> b P | $ | Q
               Q -> c Q | $"""
    expected_ecfg_prod = {
        Variable("P"): Regex("((Q|(b.P))|$)"),
        Variable("S"): Regex("(($|(a.S))|P)"),
        Variable("Q"): Regex("((c.Q)|$)"),
    }

    actual_ecfg = ecfg_from_text(cfg_text)
    expected_ecfg = ECFG(expected_ecfg_prod.keys(), expected_ecfg_prod)
    compare_ecfg(actual_ecfg, expected_ecfg)


def test_from_file():
    actual_ecfg = ecfg_from_file(Path("tests/cfg/test1"), Variable("S"))
    # cfg in file: '''S -> a S b S | x S y S | $'''
    expected_ecfg_prod = {Variable("S"): Regex("(((x.(S.(y.S)))|$)|(a.(S.(b.S))))")}
    expected_ecfg = ECFG(expected_ecfg_prod.keys(), expected_ecfg_prod)
    compare_ecfg(actual_ecfg, expected_ecfg)
