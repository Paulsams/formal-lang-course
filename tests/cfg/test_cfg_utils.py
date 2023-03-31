from pyformlang.cfg import Terminal
from project.cfg_utils import *


def test_cfg():
    first = read_cfg(Path("test1"))
    second = cfg_to_wcnf(first)
    right_words = ["", "ab", "xy", "abxyaxybxaby", "xaxaaxybaxybbyby"]
    wrong_words = ["first", "ba", "y", "yx", "axby"]
    assert all(
        all([first.contains(word), second.contains(word)]) for word in right_words
    )
    assert all(
        all([not first.contains(word), not second.contains(word)])
        for word in wrong_words
    )

    def is_normal_form_production(prod):
        if len(prod.body) == 2:
            return isinstance(prod.body[0], Variable) and isinstance(
                prod.body[1], Variable
            )
        if len(prod.body) == 1:
            return isinstance(prod.body[0], Terminal)
        return len(prod.body) == 0

    return all(
        [is_normal_form_production(production) for production in second.productions]
    )
