from pathlib import Path

from antlr4 import *
from antlr4.InputStream import InputStream
from antlr4.error.Errors import ParseCancellationException
from antlr4.tree.Tree import TerminalNodeImpl

from pydot import Dot, Edge, Node

from project.my_language.dist.GrammarLexer import GrammarLexer as Lexer
from project.my_language.dist.GrammarParser import GrammarParser as Parser
from project.my_language.dist.GrammarListener import GrammarListener as Listener


class GraphTreeListener(Listener):
    def __init__(self, text: str):
        parser = build_parser(text)
        self.ast = parser.program()
        if parser.getNumberOfSyntaxErrors() != 0:
            raise ParseCancellationException(f"Parse text: {text} -- failed")
        self.tree = Dot("language_graph", graph_type="digraph")
        self.number_nodes = 0
        self.nodes = {}
        self.rules = Parser.ruleNames
        super(GraphTreeListener, self).__init__()

    def save_in_dot(self, path: Path):
        """
        :param path: path for save of graph
        """
        ParseTreeWalker().walk(self, self.ast)
        self.tree.write(path)

    def enterEveryRule(self, rule: ParserRuleContext):
        if rule not in self.nodes:
            self.number_nodes += 1
            self.nodes[rule] = self.number_nodes
        if rule.parentCtx:
            self.tree.add_edge(Edge(self.nodes[rule.parentCtx], self.nodes[rule]))

        label = self.rules[rule.getRuleIndex()]
        self.tree.add_node(Node(self.nodes[rule], label=label))

    def visitTerminal(self, node: TerminalNodeImpl):
        self.number_nodes += 1
        self.tree.add_edge(Edge(self.nodes[node.parentCtx], self.number_nodes))
        self.tree.add_node(Node(self.number_nodes, label=f"Terminal: {node.getText()}"))


def build_parser(text: str) -> Parser:
    """
    :param text: Text to check
    :return: Built parser
    """
    data = InputStream(text)
    lexer = Lexer(data)
    stream = CommonTokenStream(lexer)
    return Parser(stream)


def check_input(text: str) -> bool:
    parser = build_parser(text)
    parser.program()
    return parser.getNumberOfSyntaxErrors() == 0
