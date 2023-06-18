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
     | 'load' WS name=(STR | VAR_NAME)                                                    # expr_load
     | left=expr WS INTERSECT_DECL WS right=expr                             # expr_intersect
     | left=expr WS CONCAT_DECL WS right=expr                                # expr_concat
     | left=expr WS UNION_DECL WS right=expr                                 # expr_union
     | expr_=expr WS? STAR_DECL                                                  # expr_star

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
