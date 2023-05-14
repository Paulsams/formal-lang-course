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
     | '(' WS? expr WS? ')'
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
          | '%' str_expr
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
                         | '[' WS? args_graph WS? '->' WS? expr WS? ']'
                         ;

var_lambda_filter_graph  : ('PredicateGraph' WS)? VAR_DECL WS lambda_filter_graph_expr ;
lambda_filter_graph_expr : '(' WS? lambda_filter_graph_expr WS? ')'
                         | args_graph WS? '->' WS? '{' WS? bool_expr WS? '}'
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

ASSIGN_CHAR  : '=' ;
VAR_DECL     : VAR_NAME WS ASSIGN_CHAR ;

SET_DECL       : 'set'       |  '<'  ;
GET_DECL       : 'get'       |  '>'  ;
ADD_DECL       : 'add'       |  '+'  ;
REMOVE_DECL    : 'remove'    |  '-'  ;
MAP_DECL       : 'map'       | '<$>' ;
FILTER_DECL    : 'filter'    | '<?>' ;
INTERSECT_DECL : 'intersect' |  '|'  ;
CONCAT_DECL    : 'concat'    |  '+'  ;
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
```
## Примеры

Получение достижимых вершин из данного графа
```
graph = load %"skos" < starts {0, 1, 2, 3, 4, 5, 6, 7}
reachables = graph > reachable
```

Вывод тех пар вершин, между которыми существует путь, удовлетворяющий КС-ограничению
```
Graph graph = CFG "S -> a S b | a b"
Regex regex = Regex "a b"
print((graph & regex) > reachable)
```

Получение множества общих меток графов "wine" и "pizza"
```
wine = load %"wine"
pizza = load %"pizza"

common_labels = (wine <?> [(_, _, lb)] -> { pizza ? lb }) get edges
print(common_labels)
```
