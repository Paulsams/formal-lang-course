from typing import Dict, Type

from project.my_language.dist.GrammarParser import GrammarParser
from project.my_language.dist.GrammarVisitor import GrammarVisitor
from project.my_language.values import *
from project.graph_utils import *
from project.my_language.saver_to_dot import build_parser


class WrongCountArgumentsException(Exception):
    def __init__(self, actual: int, excepted: int):
        self.message = (
            f"Incorrect number of arguments: left: {actual} and right:{excepted}"
        )


class InvalidArgumentException(Exception):
    def __init__(self, actual_type: Type, checked_type: Type):
        self.message = f"This type was expected: {checked_type}, but another one came: {actual_type}"


class BaseOutput:
    def write(self, text: str):
        pass

    def write_error(self, text: str):
        pass


def interpreter(program: str, output: BaseOutput):
    """
    Causes the execution of the program
    :param program: Executable program in the form of a string
    :param output: Object where errors and output will be written
    """
    parser = build_parser(program)
    tree = parser.program()
    visitor = InterpretVisitor(output)

    if parser.getNumberOfSyntaxErrors() != 0:
        output.write_error("syntax errors found")
        return

    try:
        visitor.visit(tree)
    except Exception as exception:
        output.write_error(str(exception))


def check_type(value: any, checked_type: Type):
    if not isinstance(value, checked_type):
        raise InvalidArgumentException(type(value), checked_type)


def check_types(value: any, checked_types: List[Type]):
    isInstanced: bool = False
    for iter_type in checked_types:
        if isinstance(value, iter_type):
            isInstanced = True
            break

    if not isInstanced:
        raise InvalidArgumentException(type(value), checked_types)


def check_eq_types(left: any, right: any):
    if type(left) != type(right):
        raise InvalidArgumentException(left, right)


def get_graph_from_value(value: BaseValue) -> GraphValue:
    check_types(value, [GraphValue, RegexValue])

    if isinstance(value, RegexValue):
        return create_graph_value_from_enfa(fa.build_dfa_from_regex(str(value.value)))
    else:
        return value


class InterpretVisitor(GrammarVisitor):
    vars: Dict[str, BaseValue] = {}

    def __init__(self, output: BaseOutput):
        self.output = output
        self.vars["true"] = BoolValue(True)
        self.vars["false"] = BoolValue(False)

    def recursive_pattern(self, pattern: PatternValue, elem: BaseValue):
        if pattern.value is None:
            return
        elif isinstance(pattern.value, str):
            self.vars[pattern.value] = elem
        else:
            tupleValue: TupleValue = elem
            check_type(tupleValue, TupleValue)

            for j in range(len(pattern.value)):
                self.recursive_pattern(pattern.value[j], tupleValue.value[j])

    def iterate_with_func(
        self,
        func_value: LambdaValue,
        elems_value: Union[ListValue, StringValue],
        functor,
    ):
        check_type(func_value, LambdaValue)

        args: ListValue = func_value.args
        if len(args.value) != 1:
            raise WrongCountArgumentsException(len(args.value), 1)

        check_types(elems_value, [ListValue, StringValue])

        oldVars = self.vars
        self.vars = oldVars.copy()

        pattern: PatternValue = args.value[0]
        for elem in elems_value.value:
            self.recursive_pattern(pattern, elem)
            isBreak: bool = functor(elem)
            if (isBreak is not None) and isBreak:
                break

        self.vars = oldVars

    # Visit a parse tree produced by GrammarParser#program.
    def visitProgram(self, ctx: GrammarParser.ProgramContext):
        for statement in ctx.statements:
            statement.accept(self)

    # Visit a parse tree produced by GrammarParser#statement_decl_matching.
    def visitStatement_decl(self, ctx: GrammarParser.Statement_declContext):
        self.recursive_pattern(ctx.pattern_.accept(self), ctx.value.accept(self))

    # Visit a parse tree produced by GrammarParser#statement_print.
    def visitStatement_print(self, ctx: GrammarParser.Statement_printContext):
        value = ctx.printable.accept(self)
        self.output.write(str(value))
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GrammarParser#expr_map.
    def visitExpr_map(self, ctx: GrammarParser.Expr_mapContext):
        funcValue: LambdaValue = ctx.func.accept(self)
        newValues = []

        def add_new_value(elem):
            newValue: BaseValue = funcValue.body.accept(self)
            newValues.append(newValue)

        self.iterate_with_func(
            ctx.func.accept(self), ctx.container.accept(self), add_new_value
        )
        return ListValue(newValues)

    # Visit a parse tree produced by GrammarParser#expr_add_edges.
    def visitExpr_add_edges(self, ctx: GrammarParser.Expr_add_edgesContext):
        graphValue: GraphValue = ctx.left.accept(self)
        check_type(graphValue, GraphValue)

        added_edges: ListValue = ctx.edges.accept(self)
        check_type(added_edges.value, List[EdgeValue])

        for edge in added_edges.value:
            graphValue.value.add_edge(edge.from_, edge.to, edge.label)

        return graphValue

    # Visit a parse tree produced by GrammarParser#expr_var.
    def visitExpr_var(self, ctx: GrammarParser.Expr_varContext):
        return self.vars[ctx.var.text]

    # Visit a parse tree produced by GrammarParser#expr_load.
    def visitExpr_load(self, ctx: GrammarParser.Expr_loadContext):
        if ctx.name.text[0] == '"' and ctx.name.text[-1] == '"':
            nameGraph = ctx.name.text[1:-1]
        else:
            nameGraph: StringValue = self.vars[ctx.name]
            check_type(nameGraph, StringValue)
            nameGraph: str = nameGraph.value

        graphValue = GraphValue(graph=load_graph(nameGraph))
        return graphValue

    # Visit a parse tree produced by GrammarParser#expr_remove_nodes.
    def visitExpr_remove_nodes(self, ctx: GrammarParser.Expr_remove_nodesContext):
        graphValue: GraphValue = ctx.left.accept(self)
        check_type(graphValue, GraphValue)

        added_nodes: ListValue = ctx.edges.accept(self)
        check_type(added_nodes.value, List[IntValue])

        for node in added_nodes.value:
            graphValue.value.add_node(node.value)

        return graphValue

    # Visit a parse tree produced by GrammarParser#expr_get_reachable.
    def visitExpr_get_reachable(self, ctx: GrammarParser.Expr_get_reachableContext):
        graphValue: GraphValue = ctx.graph.accept(self)
        check_type(graphValue, GraphValue)
        return graphValue.get_reachable()

    # Visit a parse tree produced by GrammarParser#expr_remove_start_nodes.
    def visitExpr_remove_start_nodes(
        self, ctx: GrammarParser.Expr_remove_start_nodesContext
    ):
        graphValue: GraphValue = ctx.left.accept(self)
        check_type(graphValue, GraphValue)

        nodes: ListValue = ctx.start_nodes.accept(self)
        check_type(nodes.value, List[int])

        return graphValue.remove_start_nodes(nodes.value)

    # Visit a parse tree produced by GrammarParser#expr_get_element_in_tuple.
    def visitExpr_get_element_in_tuple(
        self, ctx: GrammarParser.Expr_get_element_in_tupleContext
    ):
        tupleValue: TupleValue = ctx.tuple_.accept(self)
        check_type(tupleValue, TupleValue)

        return tupleValue.value[int(ctx.index.text)]

    # Visit a parse tree produced by GrammarParser#expr_concat.
    def visitExpr_concat(self, ctx: GrammarParser.Expr_concatContext):
        left: GraphValue = get_graph_from_value(ctx.left.accept(self))
        right: GraphValue = get_graph_from_value(ctx.right.accept(self))

        return left.concat(right)

        # Visit a parse tree produced by GrammarParser#expr_filter.

    def visitExpr_filter(self, ctx: GrammarParser.Expr_filterContext):
        funcValue: LambdaValue = ctx.func.accept(self)
        newValues = []

        def filter_value(elem):
            checkValue: BoolValue = funcValue.body.accept(self)
            check_type(checkValue, BoolValue)
            if checkValue.value:
                newValues.append(elem)

        self.iterate_with_func(
            ctx.func.accept(self), ctx.container.accept(self), filter_value
        )
        return ListValue(newValues)

    # Visit a parse tree produced by GrammarParser#expr_braces.
    def visitExpr_braces(self, ctx: GrammarParser.Expr_bracesContext):
        return ctx.expr_.accept(self)

    # Visit a parse tree produced by GrammarParser#expr_regex.
    def visitExpr_regex(self, ctx: GrammarParser.Expr_regexContext):
        regex: RegexValue = ctx.regex.accept(self)
        check_type(regex, RegexValue)
        return regex

    # Visit a parse tree produced by GrammarParser#expr_or.
    def visitExpr_or(self, ctx: GrammarParser.Expr_orContext):
        leftValue: BoolValue = ctx.left.accept(self)
        check_type(leftValue, BoolValue)
        rightValue: BoolValue = ctx.left.accept(self)
        check_type(rightValue, BoolValue)

        return leftValue.or_(rightValue)

    # Visit a parse tree produced by GrammarParser#expr_new_graph.
    def visitExpr_new_graph(self, ctx: GrammarParser.Expr_new_graphContext):
        nodes: ListValue = ctx.nodes.accept(self)
        check_type(nodes, ListValue)
        edges: ListValue = ctx.edges.accept(self)
        check_type(edges, ListValue)

        if ctx.start_nodes is None:
            start_nodes = None
        else:
            start_nodes = ctx.start_nodes.accept(self)
            check_type(start_nodes, ListValue)
        if ctx.final_nodes is None:
            final_nodes = None
        else:
            final_nodes = ctx.final_nodes.accept(self)
            check_type(final_nodes, ListValue)

        return GraphValue(
            nodes=nodes.value,
            edges=edges.value,
            start_nodes=start_nodes,
            final_nodes=final_nodes,
        )

    # Visit a parse tree produced by GrammarParser#expr_and.
    def visitExpr_and(self, ctx: GrammarParser.Expr_andContext):
        leftValue: BoolValue = ctx.left.accept(self)
        check_type(leftValue, BoolValue)
        rightValue: BoolValue = ctx.left.accept(self)
        check_type(rightValue, BoolValue)

        return leftValue.and_(rightValue)

    # Visit a parse tree produced by GrammarParser#expr_not.
    def visitExpr_not(self, ctx: GrammarParser.Expr_notContext):
        leftValue: BoolValue = ctx.expr_.accept(self)
        check_type(leftValue, BoolValue)

        return leftValue.not_()

    # Visit a parse tree produced by GrammarParser#expr_union.
    def visitExpr_union(self, ctx: GrammarParser.Expr_unionContext):
        left: GraphValue = get_graph_from_value(ctx.left.accept(self))
        right: GraphValue = get_graph_from_value(ctx.right.accept(self))

        return left.union(right)

    # Visit a parse tree produced by GrammarParser#expr_equals.
    def visitExpr_equals(self, ctx: GrammarParser.Expr_equalsContext):
        left: BaseValue = ctx.left.accept(self)
        right: BaseValue = ctx.left.accept(self)
        check_eq_types(left, right)

        return BoolValue(left == right)

    # Visit a parse tree produced by GrammarParser#expr_intersect.
    def visitExpr_intersect(self, ctx: GrammarParser.Expr_intersectContext):
        left: GraphValue = get_graph_from_value(ctx.left.accept(self))
        right: GraphValue = get_graph_from_value(ctx.right.accept(self))

        return left.intersect(right)

    # Visit a parse tree produced by GrammarParser#expr_star.
    def visitExpr_star(self, ctx: GrammarParser.Expr_starContext):
        graphValue: GraphValue = ctx.expr_.accept(self)
        check_type(graphValue, GraphValue)

        return graphValue.kleene_star()

    # Visit a parse tree produced by GrammarParser#expr_add_nodes.
    def visitExpr_add_nodes(self, ctx: GrammarParser.Expr_add_nodesContext):
        graphValue: GraphValue = ctx.left.accept(self)
        check_type(graphValue, GraphValue)

        nodes: ListValue = ctx.edges.accept(self)
        check_type(nodes, ListValue)

        for node in nodes.value:
            graphValue.value.add_node(node)

        return graphValue

    # Visit a parse tree produced by GrammarParser#expr_set_final_nodes.
    def visitExpr_set_final_nodes(self, ctx: GrammarParser.Expr_set_final_nodesContext):
        graphValue: GraphValue = ctx.left.accept(self)
        check_type(graphValue, GraphValue)
        nodes: ListValue = ctx.edges.accept(self)
        check_type(nodes, ListValue)

        graphValue.set_final_nodes(nodes.value)
        return graphValue

    # Visit a parse tree produced by GrammarParser#expr_contains.
    def visitExpr_contains(self, ctx: GrammarParser.Expr_containsContext):
        container = ctx.left.accept(self)
        check_types(container, [ListValue, StringValue])
        value = ctx.right.accept(self)
        return BoolValue(value in container.value)

    # Visit a parse tree produced by GrammarParser#expr_check_any.
    def visitExpr_check_any(self, ctx: GrammarParser.Expr_check_anyContext):
        funcValue: LambdaValue = ctx.func.accept(self)
        result: BoolValue = BoolValue(False)

        def check(elem):
            result.value = funcValue.body.accept(self)
            return result.value

        self.iterate_with_func(ctx.func.accept(self), ctx.container.accept(self), check)
        return result

    # Visit a parse tree produced by GrammarParser#expr_check_all.
    def visitExpr_check_all(self, ctx: GrammarParser.Expr_check_allContext):
        funcValue: LambdaValue = ctx.func.accept(self)
        result: BoolValue = BoolValue(True)

        def check(elem):
            result.value = funcValue.body.accept(self)
            return not result.value

        self.iterate_with_func(ctx.func.accept(self), ctx.container.accept(self), check)
        return result

    # Visit a parse tree produced by GrammarParser#expr_add_final_nodes.
    def visitExpr_add_final_nodes(self, ctx: GrammarParser.Expr_add_final_nodesContext):
        graphValue: GraphValue = ctx.left.accept(self)
        check_type(graphValue, GraphValue)
        nodes: ListValue = ctx.edges.accept(self)
        check_type(nodes, ListValue)

        graphValue.add_final_nodes(nodes.value)
        return graphValue

    # Visit a parse tree produced by GrammarParser#expr_get_edges.
    def visitExpr_get_edges(self, ctx: GrammarParser.Expr_get_edgesContext):
        graphValue: GraphValue = ctx.graph.accept(self)
        check_type(graphValue, GraphValue)

        return graphValue.get_edges()

    # Visit a parse tree produced by GrammarParser#expr_get_label.
    def visitExpr_get_label(self, ctx: GrammarParser.Expr_get_labelContext):
        edgeValue: EdgeValue = ctx.edge.accept(self)
        check_type(edgeValue, EdgeValue)

        return self.visitChildren(ctx)

    # Visit a parse tree produced by GrammarParser#expr_get_start_nodes.
    def visitExpr_get_start_nodes(self, ctx: GrammarParser.Expr_get_start_nodesContext):
        graphValue: GraphValue = ctx.graph.accept(self)
        check_type(graphValue, GraphValue)

        return ListValue(graphValue.start_nodes)

    # Visit a parse tree produced by GrammarParser#expr_remove_edges.
    def visitExpr_remove_edges(self, ctx: GrammarParser.Expr_remove_edgesContext):
        graphValue: GraphValue = ctx.left.accept(self)
        check_type(graphValue, GraphValue)
        edges: ListValue = ctx.edges.accept(self)
        check_type(edges.value, List[EdgeValue])

        for edge in edges.value:
            graphValue.value.remove_edge(edge)
        return graphValue

    # Visit a parse tree produced by GrammarParser#expr_get_final_nodes.
    def visitExpr_get_final_nodes(self, ctx: GrammarParser.Expr_get_final_nodesContext):
        graphValue: GraphValue = ctx.graph.accept(self)
        check_type(graphValue, GraphValue)

        return ListValue(graphValue.final_nodes)

    # Visit a parse tree produced by GrammarParser#expr_get_count.
    def visitExpr_get_count(self, ctx: GrammarParser.Expr_get_countContext):
        container = ctx.container.accept(self)
        check_types(container, [ListValue, StringValue])

        return len(container.value)

    # Visit a parse tree produced by GrammarParser#expr_literal.
    def visitExpr_literal(self, ctx: GrammarParser.Expr_literalContext):
        return ctx.value.accept(self)

    # Visit a parse tree produced by GrammarParser#expr_get_nodes.
    def visitExpr_get_nodes(self, ctx: GrammarParser.Expr_get_nodesContext):
        graphValue: GraphValue = ctx.graph.accept(self)
        check_type(graphValue, GraphValue)

        return graphValue.get_nodes()

    # Visit a parse tree produced by GrammarParser#expr_remove_final_nodes.
    def visitExpr_remove_final_nodes(
        self, ctx: GrammarParser.Expr_remove_final_nodesContext
    ):
        graphValue: GraphValue = ctx.left.accept(self)
        check_type(graphValue, GraphValue)
        nodes: ListValue = ctx.edges.accept(self)
        check_type(nodes.value, List[int])

        graphValue.remove_final_nodes(nodes.value)
        return graphValue

    # Visit a parse tree produced by GrammarParser#expr_add_start_nodes.
    def visitExpr_add_start_nodes(self, ctx: GrammarParser.Expr_add_start_nodesContext):
        graphValue: GraphValue = ctx.left.accept(self)
        check_type(graphValue, GraphValue)
        nodes: ListValue = ctx.edges.accept(self)
        check_type(nodes.value, List[IntValue])

        graphValue.add_start_nodes(nodes.value)
        return graphValue

    # Visit a parse tree produced by GrammarParser#expr_get_from_node.
    def visitExpr_get_from_node(self, ctx: GrammarParser.Expr_get_from_nodeContext):
        edgeValue: EdgeValue = ctx.edge.accept(self)
        check_type(edgeValue, EdgeValue)
        return edgeValue.from_

    # Visit a parse tree produced by GrammarParser#expr_set_start_nodes.
    def visitExpr_set_start_nodes(self, ctx: GrammarParser.Expr_set_start_nodesContext):
        graphValue: GraphValue = ctx.left.accept(self)
        check_type(graphValue, GraphValue)
        nodes: ListValue = ctx.edges.accept(self)
        check_type(nodes.value, List[int])

        graphValue.set_start_nodes(nodes.value)
        return graphValue

    # Visit a parse tree produced by GrammarParser#expr_get_labels.
    def visitExpr_get_labels(self, ctx: GrammarParser.Expr_get_labelsContext):
        graphValue: GraphValue = ctx.graph.accept(self)
        check_type(graphValue, GraphValue)

        return graphValue.get_labels()

    # Visit a parse tree produced by GrammarParser#expr_get_to_node.
    def visitExpr_get_to_node(self, ctx: GrammarParser.Expr_get_to_nodeContext):
        edgeValue: EdgeValue = ctx.edge.accept(self)
        check_type(edgeValue, EdgeValue)
        return edgeValue.to

    # Visit a parse tree produced by GrammarParser#regex_star.
    def visitRegex_star(self, ctx: GrammarParser.Regex_starContext):
        regexValue: RegexValue = ctx.regex.accept(self)
        check_type(regexValue, RegexValue)

        regexValue.kleene_star()
        return regexValue

    # Visit a parse tree produced by GrammarParser#regex_label.
    def visitRegex_label(self, ctx: GrammarParser.Regex_labelContext):
        return RegexValue(ctx.label.text)

    # Visit a parse tree produced by GrammarParser#regex_braces.
    def visitRegex_braces(self, ctx: GrammarParser.Regex_bracesContext):
        return ctx.regex.accept(self)

    # Visit a parse tree produced by GrammarParser#regex_var.
    def visitRegex_var(self, ctx: GrammarParser.Regex_varContext):
        if ctx.var.text in self.vars:
            regexValue: RegexValue = self.vars[ctx.var.text]
            check_type(regexValue, RegexValue)
        else:
            regexValue: RegexValue = RegexValue(ctx.var.text)
        return regexValue

    # Visit a parse tree produced by GrammarParser#regex_and.
    def visitRegex_and(self, ctx: GrammarParser.Regex_andContext):
        left: RegexValue = ctx.left.accept(self)
        check_type(left, RegexValue)
        right: RegexValue = ctx.right.accept(self)
        check_type(right, RegexValue)

        return left.union(right)

    # Visit a parse tree produced by GrammarParser#regex_or.
    def visitRegex_or(self, ctx: GrammarParser.Regex_orContext):
        left: RegexValue = ctx.left.accept(self)
        check_type(left, RegexValue)
        right: RegexValue = ctx.right.accept(self)
        check_type(right, RegexValue)

        return left.concat(right)

    # Visit a parse tree produced by GrammarParser#matching_vars.
    def visitPattern_matching(self, ctx: GrammarParser.Pattern_matchingContext):
        patterns = []
        for elem in list(ctx.patterns):
            patternValue: PatternValue = elem.accept(self)
            check_type(patternValue, PatternValue)
            patterns.append(patternValue)

        return PatternValue(patterns)

    # Visit a parse tree produced by GrammarParser#pattern_name.
    def visitPattern_name(self, ctx: GrammarParser.Pattern_nameContext):
        return PatternValue(ctx.name.text)

    # Visit a parse tree produced by GrammarParser#pattern_wildcard.
    def visitPattern_wildcard(self, ctx: GrammarParser.Pattern_wildcardContext):
        return PatternValue()

    # Visit a parse tree produced by GrammarParser#literal_int.
    def visitLiteral_int(self, ctx: GrammarParser.Literal_intContext):
        return IntValue(int(ctx.value.text))

    # Visit a parse tree produced by GrammarParser#literal_str.
    def visitLiteral_str(self, ctx: GrammarParser.Literal_strContext):
        return StringValue(ctx.value.text[1:-1])

    # Visit a parse tree produced by GrammarParser#literal_tuple.
    def visitLiteral_tuple(self, ctx: GrammarParser.Literal_tupleContext):
        return TupleValue(tuple(map(lambda x: x.accept(self), ctx.values)))

    # Visit a parse tree produced by GrammarParser#literal_empty_set.
    def visitLiteral_empty_set(self, ctx: GrammarParser.Literal_empty_setContext):
        return ListValue([])

    # Visit a parse tree produced by GrammarParser#literal_create_set.
    def visitLiteral_create_set(self, ctx: GrammarParser.Literal_create_setContext):
        return ListValue(list(map(lambda x: x.accept(self), ctx.values)))

    # Visit a parse tree produced by GrammarParser#literal_lambda.
    def visitLiteral_lambda(self, ctx: GrammarParser.Literal_lambdaContext):
        return LambdaValue(
            ctx.func_body, ListValue(list(map(lambda x: x.accept(self), ctx.args)))
        )
