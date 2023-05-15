grammar Grammar;

program   : EOL* ((statement WS? COMMENT? | COMMENT) WS? (EOL+ | EOF))* ;

statement : var
          | 'print' '(' WS? expr WS? ')'
          ;

expr : VAR_NAME
     | bool_expr
     | int_expr
     | str_expr
     | regex_expr
     | path_expr
     | node_expr
     | set_nodes_expr
     | set_pair_nodes_expr
     | pair_nodes_expr
     | edge_expr
     | set_edges_expr
     | label_expr
     | graph_expr
     | lambda_map_graph_expr
     | lambda_filter_graph_expr
     | graph_iter_expr
     ;

var  : var_bool
     | var_int
     | var_str
     | var_regex
     | var_path
     | var_node
     | var_set_nodes
     | var_set_pair_nodes
     | var_pair_nodes
     | var_edge
     | var_set_edges
     | var_label
     | var_graph
     | var_lambda_map_graph
     | var_lambda_filter_graph
     | var_graph_iter
     ;

// Bool
var_bool  : ('bool' WS)? VAR_DECL WS bool_expr ;
bool_expr : '(' WS? bool_expr WS? ')'
          | 'not' WS bool_expr
          | 'true' | 'false'
          | graph_expr WS CONTAINS_DECL WS (label_expr | node_expr | edge_expr)
          | node_expr WS 'in' WS set_nodes_expr
          | bool_expr WS '&&' WS bool_expr
          | bool_expr WS '||' WS bool_expr
          | str_expr WS EQUALS_CHAR WS str_expr
          | node_expr WS EQUALS_CHAR WS node_expr
          | VAR_NAME
          ;

// Int
var_int   : ('int' WS)? VAR_DECL WS int_expr ;
int_expr  : '(' WS? int_expr WS? ')'
          | INT
          // | node_expr WS GET_DECL WS 'value'
          | VAR_NAME
          ;

// String
var_str   : ('string' WS)? VAR_DECL WS str_expr ;
str_expr  : '(' WS? str_expr WS? ')'
          | STR
          | VAR_NAME
          ;

// Regex
var_regex  : ('Regex' WS)? VAR_DECL WS regex_expr ;
regex_expr : '(' WS? str_expr WS? ')'
           | 'r' STR
           | 'Regex' WS str_expr
           | VAR_NAME
           ;

// Path
var_path  : ('Path' WS)? VAR_DECL WS path_expr ;
path_expr : '(' WS? path_expr WS? ')'
          | '%' STR
          | 'Path' WS str_expr
          | VAR_NAME
          ;

// Node
var_node        : ('Node' WS)? VAR_DECL WS node_expr ;
node_expr       : '(' WS? node_expr WS? ')'
                | INT
                | edge_expr WS GET_DECL WS 'from'
                | edge_expr WS GET_DECL WS 'to'
                | pair_nodes_expr WS GET_DECL WS 'first'
                | pair_nodes_expr WS GET_DECL WS 'second'
                | VAR_NAME
                | int_expr
                ;

var_set_nodes   : ('Set<Node>' WS)? VAR_DECL WS set_nodes_expr ;
set_nodes_expr  : '(' WS? set_nodes_expr WS? ')'
                | '{' WS? '}'
                | '{' WS? (node_expr (WS? ',' WS? node_expr)* )? WS? '}'
                | graph_expr WS GET_DECL WS NODES_DECL
                | graph_expr WS GET_DECL WS START_NODES_DECL
                | graph_expr WS GET_DECL WS FINAL_NODES_DECL
                | VAR_NAME
                ;

var_set_pair_nodes  : ('Set<Pair<Node, Node>>' WS)? VAR_DECL WS set_pair_nodes_expr ;
set_pair_nodes_expr : '(' WS? set_pair_nodes_expr WS? ')'
                    | '{' WS? '}'
                    | '{' WS? (pair_nodes_expr (WS? ',' WS? pair_nodes_expr)* )? WS? '}'
                    | graph_expr WS GET_DECL WS 'reachable'
                    | VAR_NAME
                    ;

var_pair_nodes  : ('Pair<Node, Node>' WS)? VAR_NAME | '(' WS matching_var WS ',' WS matching_var WS ')' WS ASSIGN_CHAR WS pair_nodes_expr ;
pair_nodes_expr : '(' WS? pair_nodes_expr WS? ')'
                | '(' WS? node_expr WS? ',' WS? node_expr WS? ')'
                | VAR_NAME
                ;

// Edge
var_edge        : ('Edge' WS)? VAR_DECL WS edge_expr ;
edge_expr       : '(' WS? edge_expr WS? ')'
                | '(' WS? node_expr WS? ',' WS? node_expr WS? ',' WS? label_expr WS? ')'
                | VAR_NAME
                ;

var_set_edges   : ('Set<Edge>' WS)? VAR_DECL WS set_edges_expr ;
set_edges_expr  : '(' WS? set_edges_expr WS? ')'
                | '{' WS? '}'
                | '{' WS? (edge_expr (WS? ',' WS? edge_expr)* )? WS? '}'
                | graph_expr WS GET_DECL WS EDGES_DECL
                | VAR_NAME
                ;

// Label
var_label  : ('Label' WS)? VAR_DECL WS label_expr ;
label_expr : '(' WS? label_expr WS? ')'
           | STR
           | edge_expr WS GET_DECL WS 'label'
           | VAR_NAME
           | str_expr
           ;

// Graph
var_graph    : ('Graph' WS)? VAR_DECL WS graph_expr ;
graph_expr   : '(' WS? graph_expr WS? ')'
             | 'EmptyGraph'
             | 'CFG' WS str_expr
             | graph_expr WS SET_DECL WS START_NODES_DECL WS set_nodes_expr
             | graph_expr WS SET_DECL WS FINAL_NODES_DECL WS set_nodes_expr

             | graph_expr WS ADD_DECL WS NODES_DECL WS set_nodes_expr
             | graph_expr WS ADD_DECL WS START_NODES_DECL WS set_nodes_expr
             | graph_expr WS ADD_DECL WS FINAL_NODES_DECL WS set_nodes_expr
             | graph_expr WS ADD_DECL WS EDGES_DECL WS set_edges_expr

             | graph_expr WS REMOVE_DECL WS NODES_DECL WS set_nodes_expr
             | graph_expr WS REMOVE_DECL WS START_NODES_DECL WS set_nodes_expr
             | graph_expr WS REMOVE_DECL WS FINAL_NODES_DECL WS set_nodes_expr
             | graph_expr WS REMOVE_DECL WS EDGES_DECL WS set_edges_expr

             | graph_expr WS MAP_DECL WS lambda_map_graph_expr
             | graph_expr WS FILTER_DECL WS lambda_filter_graph_expr

             | 'load' WS path_expr
             | graph_expr WS INTERSECT_DECL WS graph_expr
             | graph_expr WS CONCAT_DECL WS graph_expr
             | graph_expr WS UNION_DECL WS graph_expr
             | graph_expr WS STAR_DECL WS graph_expr

             | VAR_NAME
             | regex_expr
             ;

var_lambda_map_graph     : ('ActionGraph' WS)? VAR_DECL WS lambda_map_graph_expr ;
lambda_map_graph_expr    : '(' WS? lambda_map_graph_expr WS? ')'
                         | args_graph WS? '->' WS? '{' WS? edge_expr WS? '}'
                         | VAR_NAME
                         ;

var_lambda_filter_graph  : ('PredicateGraph' WS)? VAR_DECL WS lambda_filter_graph_expr ;
lambda_filter_graph_expr : '(' WS? lambda_filter_graph_expr WS? ')'
                         | args_graph WS? '->' WS? '{' WS? bool_expr WS? '}'
                         | VAR_NAME
                         ;

var_graph_iter  : ('GraphIter' WS)? VAR_DECL WS graph_iter_expr ;
graph_iter_expr : '(' WS? graph_iter_expr WS? ')'
                | graph_expr WS GET_DECL WS 'iterator'
                | graph_iter_expr WS 'next' WS label_expr
                ;

NODES_DECL       : 'nodes'  ;
START_NODES_DECL : 'starts' ;
FINAL_NODES_DECL : 'finals' ;
EDGES_DECL       : 'edges'  ;

args_graph : '[' WS? ('(' WS? matching_var WS? ',' WS? matching_var WS? ',' WS? matching_var WS? ')' | matching_var) WS? ']' ;

matching_var : VAR_NAME | WILDCARD ;

EQUALS_CHAR  : 'eq' ;
ASSIGN_CHAR  : '='  ;
VAR_DECL     : VAR_NAME WS ASSIGN_CHAR ;

SET_DECL       : 'set'       |  '<'  ;
GET_DECL       : 'get'       |  '>'  ;
ADD_DECL       : 'add'       |  '+'  ;
REMOVE_DECL    : 'remove'    |  '-'  ;
MAP_DECL       : 'map'       | '<$>' ;
FILTER_DECL    : 'filter'    | '<?>' ;
INTERSECT_DECL : 'intersect' |  '|'  ;
CONCAT_DECL    : 'concat'    | '++'  ;
UNION_DECL     : 'union'     |  '&'  ;
STAR_DECL      : 'star'      |  '*'  ;
CONTAINS_DECL  : 'contains'  |  '?'  ;

VAR_NAME   : [a-zA-Z][a-zA-Z_0-9]* ;

WILDCARD   : '_' ;

STR     : '"' ~[\n"]* '"' ;
INT     : '0' | '-'? [1-9][0-9]* ;
COMMENT : '//' ~[\n]* ;
EOL     : ('\r'? '\n' | '\r')+ ;
WS      : (' ' | '\t')+ ;
