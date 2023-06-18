from pyformlang.finite_automaton import EpsilonNFA, NondeterministicFiniteAutomaton
from pyformlang import regular_expression as re
from typing import Union, List, Tuple
import networkx as nx

import project.finite_automatons_utils as fa


class BaseValue:
    pass


class BaseCompareValue(BaseValue):
    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __cmp__(self, other):
        return self.value.__cmp__(other.value)


class StringValue(BaseCompareValue):
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self) -> str:
        return '"' + self.value + '"'


class IntValue(BaseCompareValue):
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return str(self.value)


class LambdaValue(BaseValue):
    def __init__(self, body, args) -> None:
        self.body = body
        self.args = args

    def __str__(self) -> str:
        lam = "lambda: {"
        for x in self.args:
            lam += x.value + ", "
        if len(self.args) != 0:
            lam = lam[:-2]
        lam += "} -> body"
        return lam


class ListValue(BaseCompareValue):
    def __init__(self, lst: List):
        self.value = lst

    def __str__(self):
        output = "{"
        for elem in self.value:
            output += str(elem) + ", "
        if len(self.value) != 0:
            output = output[:-2]
        output += "}"
        return output


class TupleValue(BaseCompareValue):
    def __init__(self, value: Tuple):
        self.value = value

    def __str__(self):
        output = "("
        for elem in self.value:
            output += str(elem) + ", "
        if len(self.value) != 0:
            output = output[:-2]
        output += ")"
        return output


class PatternValue(BaseCompareValue):
    def __init__(self, value: Union[List["PatternValue"], str] = None):
        self.value = value

    def __str__(self):
        if self.value is None:
            return "_"
        elif isinstance(self.value, str):
            return self.value
        else:
            output = "("
            for elem in self.value:
                output += "_" if elem is None else str(elem) + ", "
            output += ")"
            return output


class BoolValue(BaseCompareValue):
    def __init__(self, value: bool) -> None:
        self.value = value

    def __str__(self) -> str:
        return "true" if self.value else "false"

    def and_(self, other: "BoolValue") -> "BoolValue":
        return BoolValue(self.value and other.value)

    def or_(self, other: "BoolValue") -> "BoolValue":
        return BoolValue(self.value or other.value)

    def not_(self):
        return not self.value


class EdgeValue(BaseValue):
    def __init__(self, from_: IntValue, label: StringValue, to: IntValue) -> None:
        self.from_ = from_
        self.label = label
        self.to = to

    def __str__(self) -> str:
        return "Edge: ({0}, {1}, {2})".format(self.from_, self.label, self.to)


class RegexValue(BaseCompareValue):
    def __init__(self, regex_str: str = "", regex: re.Regex = None) -> None:
        if regex is None:
            regex_str = regex_str.replace('"', "")
            regex = re.Regex(regex_str)
        self.value: re.Regex = regex

    def __str__(self) -> str:
        return self.value.__str__()

    def concat(self, regex: "RegexValue") -> "RegexValue":
        return RegexValue(regex=self.value.concatenate(regex.value))

    def union(self, regex: "RegexValue") -> "RegexValue":
        return RegexValue(regex=self.value.union(regex.value))

    def kleene_star(self) -> "RegexValue":
        return RegexValue(regex=self.value.kleene_star())

    def __eq__(self, regex: "RegexValue") -> bool:
        return self.value == regex.value


class GraphValue(BaseValue):
    def __init__(
        self,
        graph=None,
        nodes: List[IntValue] = None,
        edges: List[TupleValue] = None,
        start_nodes: List[IntValue] = None,
        final_nodes: List[IntValue] = None,
    ):
        if graph is None:
            self.value = nx.MultiDiGraph()
            for node in nodes:
                self.value.add_node(node.value)
            for edge in edges:
                self.value.add_edge(
                    edge.value[0].value, edge.value[2].value, label=edge.value[1].value
                )
        else:
            self.value = nx.MultiDiGraph(graph)

        self.start_nodes = (
            self.get_nodes() if start_nodes is None else ListValue(start_nodes)
        )
        self.final_nodes = (
            self.get_nodes() if start_nodes is None else ListValue(final_nodes)
        )

    def __str__(self) -> str:
        output = f"""Graph:
nodes: {str(self.get_nodes())}
edges: {str(self.get_edges())}"""
        return output

    def set_start_nodes(self, nodes: List[IntValue]):
        self.value.add_nodes_from(nodes)
        self.start_nodes.value = nodes

    def set_final_nodes(self, nodes: List[IntValue]):
        self.value.add_nodes_from(nodes)
        self.final_nodes.value = nodes

    def add_start_nodes(self, nodes: List[IntValue]):
        self.value.add_nodes_from(nodes)
        self.start_nodes.value += nodes

    def add_final_nodes(self, nodes: List[IntValue]):
        self.value.add_nodes_from(nodes)
        self.final_nodes.value += nodes

    def remove_start_nodes(self, nodes: List[IntValue]):
        self.value.remove_nodes_from(nodes)
        self.start_nodes.value -= nodes

    def remove_final_nodes(self, nodes: List[IntValue]):
        self.value.remove_nodes_from(nodes)
        self.final_nodes.value -= nodes

    def get_reachable(self) -> "ListValue":
        result = ListValue([])
        for s, t in nx.transitive_closure(nx.DiGraph(self.value)).edges():
            if (
                IntValue(s) in self.start_nodes.value
                and IntValue(t) in self.final_nodes.value
            ):
                result.value.append(TupleValue((IntValue(s), IntValue(t))))
        return result

    def get_nodes(self) -> ListValue:
        return ListValue(list(map(lambda x: IntValue(x), self.value.nodes)))

    def get_edges(self) -> ListValue:
        result = ListValue([])
        for (u, v, k) in self.value.edges(data=True):
            for label in k.values():
                result.value.append(
                    TupleValue((IntValue(u), StringValue(label), IntValue(v)))
                )
        return result

    def get_labels(self) -> ListValue:
        result = set()
        for _, _, l in self.value.edges(data=True):
            for label in l.values():
                result.add(StringValue(label))
        return ListValue(list(result))

    def intersect(self, other: "GraphValue") -> "GraphValue":
        second = fa.build_enfa_from_networkx_graph(
            other.value, other.start_nodes.value, other.final_nodes.value
        )
        first = fa.build_enfa_from_networkx_graph(
            self.value, self.start_nodes.value, self.final_nodes.value
        )

        result = fa.intersection_automations(first, second)
        return create_graph_value_from_enfa(result)

    def concat(self, other: "GraphValue") -> "GraphValue":
        second = (
            fa.build_enfa_from_networkx_graph(
                other.value, other.start_nodes.value, other.final_nodes.value
            )
            .minimize()
            .to_regex()
        )

        first = (
            fa.build_enfa_from_networkx_graph(
                self.value, self.start_nodes.value, self.final_nodes.value
            )
            .minimize()
            .to_regex()
        )

        result = first.concatenate(second).to_epsilon_nfa().minimize()
        return create_graph_value_from_enfa(result)

    def union(self, entity: "GraphValue") -> "GraphValue":
        second = fa.build_enfa_from_networkx_graph(
            entity.value, entity.start_nodes.value, entity.final_nodes.value
        ).minimize()

        first = fa.build_enfa_from_networkx_graph(
            self.value, self.start_nodes.value, self.final_nodes.value
        ).minimize()

        result = first.union(second).minimize()
        return create_graph_value_from_enfa(result)

    def kleene_star(self) -> "GraphValue":
        second: NondeterministicFiniteAutomaton = (
            fa.build_enfa_from_networkx_graph(
                self.value, self.start_nodes, self.final_nodes
            )
            .minimize()
            .to_regex()
        )

        result = second.kleene_star().to_epsilon_nfa().minimize()
        return create_graph_value_from_enfa(result)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GraphValue):
            return False

        return self.get_edges() == other.get_edges()


def create_graph_value_from_enfa(graph: EpsilonNFA) -> GraphValue:
    start_nodes = [x.value for x in graph.start_states]
    final_nodes = [x.value for x in graph.final_states]
    return GraphValue(
        graph=graph.to_networkx(), start_nodes=start_nodes, final_nodes=final_nodes
    )
