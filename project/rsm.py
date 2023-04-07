from typing import NamedTuple, Dict
from pyformlang.finite_automaton import EpsilonNFA
from pyformlang.cfg import Variable
import project.ecfg as ecfg_utils


class RSM(NamedTuple):
    start_symbol: Variable
    boxes: Dict[Variable, EpsilonNFA]


def rsm_from_ecfg(ecfg: ecfg_utils.ECFG) -> RSM:
    return RSM(
        ecfg.start_symbol,
        {head: body.to_epsilon_nfa() for head, body in ecfg.productions.items()},
    )


def minimize_rsm(rsm) -> RSM:
    for var, nfa in rsm.boxes.items():
        rsm.boxes[var] = nfa.minimize()
    return rsm
