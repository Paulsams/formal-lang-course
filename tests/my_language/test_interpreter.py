from project.my_language.interpreter import BaseOutput, interpreter


class OutputToStr(BaseOutput):
    text: str = ""
    error_text: str = ""

    def write(self, text: str):
        self.text += text

    def write_error(self, text: str):
        self.error_text = text
        raise text

    def clear(self):
        self.text = ""
        self.error_text = ""


def test_vars():
    output = OutputToStr()
    interpreter(
        """
    x = 33
    print(x)
    x = 423432432
    print(x)
    """,
        output,
    )

    assert output.text == "33423432432"
    output.clear()

    interpreter(
        """
    g = Graph ({1, 2, 3, 4}, {(1, "a", 2), (3, "b", 4)})
    print (g)
    """,
        output,
    )
    assert "Graph:" in output.text
    assert "nodes: {1, 2, 3, 4}" in output.text
    assert 'edges: {(1, "a", 2), (3, "b", 4)}' in output.text
    output.clear()

    interpreter(
        """
    g = Graph ({}, {})
    print (g)
    """,
        output,
    )

    assert "Graph:" in output.text
    assert "nodes: {}" in output.text
    assert "edges: {}" in output.text
    output.clear()


def test_getters():
    output = OutputToStr()
    interpreter(
        """
    graph = Graph ({1, 2, 3, 4, 5}, {(1, "c", 2), (2, "b", 3), (1, "a", 4)})
    print (graph get nodes)
    print (graph > reachable)
    print (graph get edges)
    """,
        output,
    )

    assert all(
        map(lambda x: x in output.text, ["(1, 2)", "(1, 4)", "(1, 3)", "(2, 3)"])
    )
    assert "{1, 2, 3, 4, 5}" in output.text
    assert all(
        map(lambda x: x in output.text, ['(1, "c", 2)', '(2, "b", 3)', '(1, "a", 4)'])
    )
    output.clear()


def test_map():
    output = OutputToStr()
    interpreter(
        """
    fst = ((x, y)) -> { x }
    snd = ((x, y)) -> { y }
    list = {(1, 2), (2, 3), (3, 2), (2, 1)}
    print (list map fst)
    print (list <$> snd)
    """,
        output,
    )
    assert "{1, 2, 3, 2}" in output.text
    assert "{2, 3, 2, 1}" in output.text
    output.clear()

    interpreter(
        """
    id = (z) -> { z }
    first = Graph ({1, 2, 3, 4}, {(1, "a", 2), (3, "c", 4)})
    second = Graph ({5, 7, 9, 10}, {(5, "a", 7), (9, "c", 10)})
    list = {first, second}
    print (list <$> id)
    """,
        output,
    )

    assert "{1, 2, 3, 4}" in output.text
    assert "{5, 7, 9, 10}" in output.text


def test_filter():
    output = OutputToStr()
    interpreter(
        """
    get_only_have_a = (graph) -> { (graph > labels) contains "a" }
    getter_labels = (graph) -> { graph > labels }
    first = Graph ({1, 2, 3, 4}, {(1, "a", 2), (3, "c", 4)})
    second = Graph ({5, 7, 9, 10}, {(5, "z", 7), (9, "c", 10)})
    list = {first, second}
    list = (list <?> get_only_have_a)
    print (list <$> getter_labels)
    """,
        output,
    )
    assert "a" in output.text


def test_load():
    output = OutputToStr()

    interpreter(
        """
    graph = load "skos"
    print ((graph > edges) > count)
    """,
        output,
    )
    assert output.text == "252"
    output.clear()

    interpreter(
        """
    graph = load "pizza"
    print ((graph > nodes) > count)
    """,
        output,
    )
    assert output.text == "671"
    output.clear()


def test_binary_op_from_graph():
    output = OutputToStr()
    interpreter(
        """
    graph = Graph ({0, 1, 2, 3}, {(0, "a", 3), (3, "b", 0), (0, "a", 1), (1, "b", 2), (3, "b", 2), (2, "a", 0)})
    regex1 = a* b
    regex2 = c regex1
    graph = graph & regex1
    graph = graph | regex2
    print (graph)
    print (graph > reachable)
    """,
        output,
    )
    output.clear()


def test_pattern_matching():
    output = OutputToStr()
    interpreter(
        """
    (b, i, s) = (true, 10, "fifa")
    print((b, i, s))
    """,
        output,
    )
    assert output.text == '(true, 10, "fifa")'
    output.clear()

    interpreter(
        """
    (b, (i1, (i2, s2)), s1) = (true, (10, (12, "pipa")), "fifa")
    print((b, (i1, (i2, s2)), s1))
    """,
        output,
    )
    assert output.text == '(true, (10, (12, "pipa")), "fifa")'
