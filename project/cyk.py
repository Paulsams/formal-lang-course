from pyformlang.cfg import CFG


def cyk(cfg: CFG, text: str) -> bool:
    """
    Check whether CFG accepts given text from Cocke-Younger-Kasami algorithm
    """
    text_len = len(text)

    if not text_len:
        return cfg.generate_epsilon()

    cnf = cfg.to_normal_form()

    term_productions = []
    var_productions = []
    for p in cnf.productions:
        if len(p.body) == 1:
            term_productions.append(p)
        elif len(p.body) == 2:
            var_productions.append(p)

    m = [[set() for _ in range(text_len)] for _ in range(text_len)]

    for i in range(text_len):
        m[i][i].update(
            production.head.value
            for production in term_productions
            if text[i] == production.body[0].value
        )

    for step in range(1, text_len):
        for i in range(text_len - step):
            j = i + step
            for k in range(i, j):
                m[i][j].update(
                    production.head.value
                    for production in var_productions
                    if production.body[0].value in m[i][k]
                    and production.body[1].value in m[k + 1][j]
                )

    return cnf.start_symbol.value in m[0][text_len - 1]
