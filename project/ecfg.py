from pathlib import Path
from typing import NamedTuple, Dict, AbstractSet

from pyformlang.cfg import Variable
from pyformlang.cfg import CFG
from pyformlang.regular_expression import Regex


class ECFG(NamedTuple):
    variables: AbstractSet[Variable]
    productions: Dict[Variable, Regex]
    start_symbol: Variable = Variable("S")


def ecfg_from_cfg(cfg: CFG) -> ECFG:
    """
    Convert CFG to ECFG
    """
    variables = set(cfg.variables)
    start_symbol = Variable("S") if cfg.start_symbol is None else cfg.start_symbol
    variables.add(start_symbol)

    productions = {}
    for prod in cfg.productions:
        body = Regex(
            " ".join(cfgObj.value for cfgObj in prod.body)
            if len(prod.body) > 0
            else "$"
        )
        productions[prod.head] = (
            productions[prod.head].union(body) if prod.head in productions else body
        )

    return ECFG(variables, productions, start_symbol)


def ecfg_from_text(text: str, start_symbol=Variable("S")) -> ECFG:
    """
    Convert text to ECFG
    """
    variables = set()
    productions = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        head, body = line.split("->")
        head = Variable(head.strip())
        variables.add(head)
        productions[head] = Regex(body)
    return ECFG(variables, productions, start_symbol)


def ecfg_from_file(path: Path, start_symbol=Variable("S")) -> ECFG:
    """
    Open file from given path and convert text from it into ECFG
    """
    with open(path, "r") as func:
        data = func.read()
    return ecfg_from_text(data, start_symbol)
