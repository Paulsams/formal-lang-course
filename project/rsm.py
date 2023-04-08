from typing import NamedTuple, Dict, Any
from pyformlang.finite_automaton import EpsilonNFA
from pyformlang.cfg import Variable
import project.ecfg as ecfg_utils
from project.finite_automatons_utils import get_states_and_matrix_from_nfa
from scipy.sparse import dok_matrix


class RSM(NamedTuple):
    start_symbol: Variable
    boxes: Dict[Variable, EpsilonNFA]


def rsm_from_ecfg(ecfg: ecfg_utils.ECFG) -> RSM:
    """
    Convert RSM from ECFG
    """
    return RSM(
        ecfg.start_symbol,
        {head: body.to_epsilon_nfa() for head, body in ecfg.productions.items()},
    )


def create_boolean_decomposition_from_rsm(
    rsm: RSM,
) -> Dict[Variable, Dict[Any, dok_matrix]]:
    """
    Convert to boolean decomposition from rsm
    """
    decompositions = {}
    for key, value in rsm.boxes.items():
        decompositions[key] = get_states_and_matrix_from_nfa(value)[1]
    return decompositions


def minimize_rsm(rsm: RSM) -> RSM:
    """
    Return minimize RSM
    """
    for var, nfa in rsm.boxes.items():
        rsm.boxes[var] = nfa.minimize()
    return rsm
