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
grammar Grammar;

program   : (WS* EOL)* ((WS* statements+=statement WS? COMMENT? | COMMENT) WS? (EOL+ | EOF))* WS* ;

statement : pattern_=pattern WS ASSIGN_CHAR WS value=expr          # statement_decl
          | 'print' WS? '(' WS? printable=expr WS? ')'             # statement_print
          ;

expr : var=VAR_NAME                                                          # expr_var
     | value=literal                                                         # expr_literal
     | '(' WS? expr_=expr WS? ')'                                            # expr_braces
     // Создание графа
     | 'Graph' WS? '(' WS? nodes=expr WS? ',' WS? edges=expr WS?
        (',' WS? start_nodes=expr WS?)? (',' WS? final_nodes=expr WS?)? ')'  # expr_new_graph
     | regex=regex_expr                                                      # expr_regex
     | 'load' WS name=STR                                                    # expr_load
     | left=expr WS INTERSECT_DECL WS right=expr                             # expr_intersect
     | left=expr WS CONCAT_DECL WS right=expr                                # expr_concat
     | left=expr WS UNION_DECL WS right=expr                                 # expr_union
     | expr_=expr STAR_DECL                                                  # expr_star

     // Модицификация графа
     | left=expr WS SET_DECL WS START_NODES_DECL WS start_nodes=expr         # expr_set_start_nodes
     | left=expr WS SET_DECL WS FINAL_NODES_DECL WS final_nodes=expr         # expr_set_final_nodes

     | left=expr WS ADD_DECL WS NODES_DECL WS nodes=expr                     # expr_add_nodes
     | left=expr WS ADD_DECL WS START_NODES_DECL WS start_nodes=expr         # expr_add_start_nodes
     | left=expr WS ADD_DECL WS FINAL_NODES_DECL WS final_nodes=expr         # expr_add_final_nodes
     | left=expr WS ADD_DECL WS EDGES_DECL WS edges=expr                     # expr_add_edges

     | left=expr WS REMOVE_DECL WS NODES_DECL WS nodes=expr                  # expr_remove_nodes
     | left=expr WS REMOVE_DECL WS START_NODES_DECL WS start_nodes=expr      # expr_remove_start_nodes
     | left=expr WS REMOVE_DECL WS FINAL_NODES_DECL WS final_nodes=expr      # expr_remove_final_nodes
     | left=expr WS REMOVE_DECL WS EDGES_DECL WS edges=expr                  # expr_remove_edges

     // Функторы над выражениями
     | container=expr WS MAP_DECL WS func=expr                               # expr_map
     | container=expr WS FILTER_DECL WS func=expr                            # expr_filter

     // Лейбл
     | edge=expr WS GET_DECL WS 'label'                                      # expr_get_label

     // Множества
     | graph=expr WS GET_DECL WS EDGES_DECL                                  # expr_get_edges
     | graph=expr WS GET_DECL WS 'reachable'                                 # expr_get_reachable
     | graph=expr WS GET_DECL WS NODES_DECL                                  # expr_get_nodes
     | graph=expr WS GET_DECL WS 'labels'                                    # expr_get_labels
     | graph=expr WS GET_DECL WS START_NODES_DECL                            # expr_get_start_nodes
     | graph=expr WS GET_DECL WS FINAL_NODES_DECL                            # expr_get_final_nodes
     | container=expr WS GET_DECL WS 'count'                                 # expr_get_count

     // Таплы
     | tuple=expr WS GET_DECL WS '^_' index=INT                              # expr_get_element_in_tuple

     // Едж
     | edge=expr WS GET_DECL WS 'from'                                       # expr_get_from_node
     | edge=expr WS GET_DECL WS 'to'                                         # expr_get_to_node

     // Бул
     | left=expr WS EQUALS_CHAR WS right=expr                                # expr_equals
     | left=expr WS CONTAINS_DECL WS right=expr                              # expr_contains
     | left=expr WS 'any' WS right=expr                                      # expr_check_all
     | left=expr WS 'all' WS right=expr                                      # expr_check_any
     | left=expr WS '&&' WS right=expr                                       # expr_and
     | left=expr WS '||' WS right=expr                                       # expr_or
     | 'not' WS expr_=expr                                                   # expr_not
     ;

regex_expr : '(' regex=regex_expr ')'                                        # regex_braces
           | var=VAR_NAME                                                    # regex_var
           | regex=regex_expr '*'                                            # regex_star
           | left=regex_expr WS? 'r|' WS? right=regex_expr                   # regex_or
           | left=regex_expr WS right=regex_expr                             # regex_and
           | label=STR                                                       # regex_label
           ;

pattern : name=VAR_NAME                                                          # pattern_name
        | WILDCARD                                                               # pattern_wildcard
        | '(' WS? (patterns+=pattern (WS? ',' WS? patterns+=pattern)* )? WS? ')' # pattern_matching
        ;

literal : value=INT                                                                              # literal_int
        | value=STR                                                                              # literal_str
        // Тапл
        | '(' WS? (values+=expr WS? ',' WS? values+=expr (WS? ',' WS? values+=expr)? )? WS? ')'  # literal_tuple
        // Множества
        | '{' WS? '}'                                        # literal_empty_set
        | '{' WS? (values+=expr (WS? ',' WS? values+=expr)* )? WS? '}'                           # literal_create_set
        // Лямбды
        | '(' WS? (args+=pattern (WS? ',' WS? args+=pattern)* )? WS? ')' WS? '->' WS?
          '{' WS? func_body=expr WS? '}'                                                         # literal_lambda
        ;

NODES_DECL       : 'nodes'  ;
START_NODES_DECL : 'starts' ;
FINAL_NODES_DECL : 'finals' ;
EDGES_DECL       : 'edges'  ;

EQUALS_CHAR  : 'eq' ;
ASSIGN_CHAR  : '='  ;

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
```

## Система типов

Доступные типы перечислены в таблице.

| Тип 	  | Краткое описание    | Пример синтаксиса                      |
|--------|---------------------|----------------------------------------|
| Int    | Целочисленный тип   | 10                                     |
| String | Строка              | "Hello!!!"                             |
| Edge   | Ребро графа         | (from, label, to)                      |
| Graph  | Граф                | {{ноды}, {набор ребёр}}                |
| Regex  | Регулярное выражение | a* (b \| c) \| a d                     | c)                                   |
| Bool   | Логический тип      | true или false                         |
| Lambda | Lambda функция      | ((from, label , to) -> { (1, "c", 2) }) |
| Tuple  | Кортеж              | (..., 4, "fs", true, ...)              |
| List   | Лист                | {..., 4, 5, 6, ...}                    |

Тип `Edge` самому создать нельзя.

## Примеры

Получение достижимых вершин из данного графа
```
graph = load "skos" < starts {0, 1, 2, 3, 4, 5, 6, 7}
reachables = graph > reachable
```

Вывод тех пар вершин, между которыми существует путь, удовлетворяющий КС-ограничению
```
regex1 = a* r| b
regex2 = c a
print((regex1 & regex2) > reachable)
```

Получение множества общих меток графов "wine" и "pizza"
```
wine = load "wine"
pizza = load "pizza"

common_labels = (wine <?> ((_, _, lb)) -> { pizza ? lb }) get edges
print(common_labels)
```
