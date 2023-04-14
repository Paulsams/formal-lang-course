import pytest
from pyformlang.cfg import CFG
from project.cyk import cyk


def test_is_string_deducible_from_grammar():
    def test_impl(cfg_text, actual, excepted):
        cfg = CFG.from_text(cfg_text)
        assert all(cyk(cfg, text) for text in actual)
        assert all(not cyk(cfg, text) for text in excepted)

    test_impl(
        "S -> a S b S | x S y S | $",
        {"", "ab", "xy", "abxyaxybxaby", "xaxaaxybaxybbyby"},
        {"a", "ba", "y", "yx", "axby"},
    )

    test_impl(
        "S -> a S | P\nP -> b P | Q\nQ -> c Q | c",
        {"c", "abc", "acc", "aaaaabccccc", "abccc"},
        {"", "ca", "acb", "ab", "aaaaaabbbbb"},
    )
