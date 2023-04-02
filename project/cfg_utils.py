from pathlib import Path
from pyformlang.cfg import CFG, Variable


def cfg_str_to_wcnf(cfg: str, start: str = "S") -> CFG:
    """
    A more convenient function for translating cfg to wcnf
    """
    return cfg_to_wcnf(CFG.from_text(cfg, Variable(start)))


def cfg_to_wcnf(cfg: CFG) -> CFG:
    """
    Translating cfg to wcnf
    :param cfg:
    :return:
    """
    temp = cfg.eliminate_unit_productions().remove_useless_symbols()
    new = temp._get_productions_with_only_single_terminals()
    new = temp._decompose_productions(new)
    return CFG(start_symbol=cfg._start_symbol, productions=set(new))


def read_cfg(path: Path, start: str = "S") -> CFG:
    """
    Reading cfg from a file
    """
    with open(path, "r") as func:
        data = func.read()
    return CFG.from_text(data, Variable(start))
