# Cинтаксиса языка запросов к графам

## Абстрактный синтаксис

```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val =
    Bool of bool
  | Int of int
  | String of string
  | Regex of regex
  | Path of path
  | Node of int
  | Edge of Tuple<Node, Node, Label>
  | Set of Set<T>
  | PairNodes of Pair<Node, Node>
  | Graph of graph
  | GraphIter of GraphIterator

expr =
    Var of var                   // переменные
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr * expr     // получить множество стартовых состояний
  | Get_final of expr * expr     // получить множество финальных состояний
  | Get_reachable of expr * expr // получить все пары достижимых вершин
  | Get_vertices of expr * expr  // получить все вершины
  | Get_edges of expr * expr     // получить все рёбра
  | Get_labels of expr * expr    // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path * expr          // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr * expr          // замыкание языков (звезда Клини)
  | Smb of expr * expr           // единичный переход
  | Contains of expr             // проверить, что есть ли в графе такое ребро, метка или нода

lambda = Lambda of List<argument> * expr

argument =
    Wildcard                                 // значение не нужно
  | Name of string                           // именованное значение
```

## Конкретный синтаксис
```
prog : (COMMENT? EOL | stmt? COMMENT? (EOL | EOF))*

stmt : var
     | 'print' '(' expr ')'

expr : '(' WS expr WS ')'
     | bool_exp
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
     | lambda_map_graph
     | lambda_filter_graph
     | graph_iter_expr

var  : var_bool
     | var_int
     | var_str
     | var_regex
     | var_path
     | var_node
     | var_set_nodes
     | var_set_pair_nodes
     | var_pair_nodes
     | var_set_edges
     | var_label_expr
     | var_graph_expr
     | var_lambda_map_graph
     | var_lambda_filter_graph
     | var_graph_iter

// Bool
var_bool  : 'bool' WS VAR_DECl WS bool_expr
bool_expr : 'true' | 'false'
          | node_expr WS 'in' WS set_nodes_expr
          | 'not' WS bool_expr
          | bool_expr WS '&&' WS bool_expr
          | bool_expr WS '||' WS bool_expr
          | graph_expr WS CONTAINS_DECL WS (label_expr | node_expr | edge_expr)
          | '(' WS bool_expr WS ')'

// Int
var_int   : 'int' WS VAR_DECl WS int_expr
int_expr  : INT
          | node_expr
          | '(' WS int_expr WS ')'

// String
var_str   : 'string' WS VAR_DECL WS str_expr
str_expr  : STR
          | '(' WS str_expr WS ')'

// Regex
var_regex  : 'Regex' WS VAR_DECL WS regex_expr
regex_expr : str_expr
           | '(' WS str_expr WS ')'

// Path
var_path  : 'Path' WS VAR_DECL WS path_expr
path_expr : str_expr
          | '(' WS path_expr WS ')'

// Node
var_node        : 'Node' WS VAR_DECL WS node_expr
node_expr       : INT
                | edge_expr WS GET_DECl WS 'from'
                | edge_expr WS GET_DECl WS 'to'
                | pair_nodes_expr WS GET_DECl WS 'first'
                | pair_nodes_expr WS GET_DECl WS 'second'
                | '(' WS node_expr WS ')'

var_set_nodes   : 'Set<Node>' WS VAR_DECl WS set_nodes_expr
set_nodes_expr  : '{' WS '}'
                | '{' WS (node_expr (',' WS node_expr)* )? WS '}'
                | graph_expr WS GET_DECL WS NODES_ACCESSOR
                | graph_expr WS GET_DECL WS START_NODES_ACCESSOR
                | graph_expr WS GET_DECL WS FINAl_NODES_ACCESSOR
                | '(' WS set_nodes_expr WS ')'

var_set_pair_nodes  : 'Set<Pair<Node, Node>>' WS VAR_DECL WS set_pair_nodes_expr
set_pair_nodes_expr : '{' WS '}'
                    | '{' WS (pair_nodes_expr (',' WS pair_nodes_expr)* )? WS '}'
                    | graph_expr WS GET_DECL WS 'reachable'

var_pair_nodes  : ('Pair<Node, Node>' WS VAR_NAME | '(' WS (VAR_NAME | WILDCARD) WS ',' WS (VAR_NAME | WILDCARD) WS ')' WS ASSIGN_CHAR WS pair_nodes_expr
pair_nodes_expr : '(' WS node WS ',' WS node WS ')'
                | '(' WS pair_nodes_expr WS ')'

// Edge
var_edge        : 'Edge' WS VAR_DECL WS edge_expr
edge_expr       : '(' WS node WS ',' WS node WS ',' WS label WS ')'
                | '(' WS edge_expr WS ')'

var_set_edges   : 'Set<Edge>' WS VAR_DECl WS set_edges_expr
set_edges_expr  : '{' WS '}'
                | '{' (edge (',' WS edge)* )? '}'
                | graph_expr GET_DECL EDGES_ACCESSOR
                | '(' WS set_edges_expr WS ')'

// Label
var_label  : 'Label' WS VAR_DECL WS label_expr
label_expr : str_expr
           | edge_expr GET_DECL 'label'
           | '(' WS label_expr WS ')'

// Graph
var_graph    : 'Graph' WS VAR_DECL WS graph_expr
graph_expr   : 'EmptyGraph'
             | 'CFG' WC str_expr
             | regex_expr
             | graph_expr WS SET_DECL WS START_NODES_ACCESSOR
             | graph_expr WS SET_DECL WS FINAl_NODES_ACCESSOR

             | graph_expr WS ADD_DECL WS NODES_ACCESSOR
             | graph_expr WS ADD_DECL WS START_NODES_ACCESSOR
             | graph_expr WS ADD_DECL WS FINAl_NODES_ACCESSOR
             | graph_expr WS ADD_DECL WS EDGES_ACCESSOR

             | graph_expr WS REMOVE_DECL WS NODES_ACCESSOR
             | graph_expr WS REMOVE_DECL WS START_NODES_ACCESSOR
             | graph_expr WS REMOVE_DECL WS FINAl_NODES_ACCESSOR
             | graph_expr WS REMOVE_DECL WS EDGES_ACCESSOR

             | graph_expr WS MAP_DECL WS lambda_map_graph
             | graph_expr WS FILTER_DECL WS lambda_filter_graph

             | 'load' WS path_expr
             | graph_expr WS INTERSECT_DECL WS graph_expr
             | graph_expr WS CONCAT_DECL WS graph_expr
             | graph_expr WS UNION_DECL WS graph_expr
             | graph_expr WS STAR_DECL WS graph_expr

             | '(' WS graph_expr WS ')'

var_lambda_map_graph    : 'ActionGraph' WS VAR_DECL WS lambda_map_graph
lambda_map_graph        : ARGS_GRAPH WS '->' WS expr
                        | '(' WS lambda_map_graph WS ')'

var_lambda_filter_graph : 'PredicateGraph' WS VAR_DECL WS lambda_filter_graph
lambda_filter_graph     : ARGS_GRAPH WS '->' WS bool_expr
                        | '(' WS lambda_filter_graph WS ')'

var_graph_iter  : VAR_DECL WS graph_iter_expr
graph_iter_expr : graph_expr WS GET_DECL WS 'iterator'
                | graph_iter_expr WS 'next' WS label
                | '(' WS graph_iter_expr WS ')'

ASSIGN_CHAR  : '='
VAR_DECl     : VAR_NAME WS ASSIGN_CHAR

SET_DECl       : 'set'       |  '<'
GET_DECL       : 'get'       |  '>'
ADD_DECL       : 'add'       |  '+'
REMOVE_DECL    : 'remove'    |  '-'
MAP_DECL       : 'map'       | '<$>'
FILTER_DECL    : 'filter'    | '<?>'
INTERSECT_DECL : 'intersect' |  '|'
CONCAT_DECL    : 'concat'    |  '+'
UNION_DECL     : 'union'     |  '&'
STAR_DECL      : 'star'      |  '*'
CONTAINS_DECL  : 'contains'  |  '?'

NODES_ACCESSOR       : 'nodes' set_nodes_expr
START_NODES_ACCESSOR : 'starts' set_nodes_expr
FINAl_NODES_ACCESSOR : 'finals' set_nodes_expr
EDGES_ACCESSOR       : 'edges' set_edges_expr

ARGS_GRAPH : '(' WS (edge_expr | VAR_NAME | WILDCARD) WS ')'

WILDCARD   : '_'

VAR_NAME -> [a-zA-Z_][a-zA-Z_0-9]*

STR     : '"' ~[\n]* '"'
INT     : '-'? [1-9][0-9]*
COMMENT : '//' ~[\n]*
EOL     : ('\r'? '\n' | '\r')+
WS      : (' ' | '\t')+
```
## Примеры

Получение достижимых вершин из данного графа
```
Graph graph = load "skos" < starts {0, 1, 2, 3, 4, 5, 6, 7}
Set<Pair<Node, Node>> reachables = graph > reachable
```

Вывод тех пар вершин, между которыми существует путь, удовлетворяющий КС-ограничению
```
Graph graph = CFG "S -> a S b | a b"
Regex regex = "a b"
print((graph & regex) > reachable)
```

Получение множества общих меток графов "wine" и "pizza"
```
Graph wine = load "wine"
Graph pizza = load "pizza"
Set<Edge> common_labels = wine filter ((_, _, label) -> label ? pizza) > edges
print(common_labels)
```
