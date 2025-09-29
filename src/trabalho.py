# Integrantes do grupo:
# Ana Maria Midori Rocha Hinoshita - anamariamidori
# Lucas Antonio Linhares - Sabuti
#
# Nome do grupo no Canvas: RA2 5

import sys # import para gerenciar argumentos de linha de comando

EPS = 'ε' # símbolo para epsilon / vazio

def construirGramatica(): # nenhuma entrada | saída: dados da gramática, FIRST, FOLLOW, tabelaLL1

    def is_nonterminal(sym, G):
        return sym in G # true se sym é um não-terminal em G, false é terminal

    def calcularFirst(G):
        FIRST = {A: set() for A in G} # inicializa FIRST para cada não-terminal com conjuntos vazios
        changed = True
        while changed:
            changed = False
            for A in G: # para cada não-terminal A. Ex: G['EXPR']
                for prod in G[A]: # para cada produção de A. Ex = [['(', 'RPN_SEQ', ')']]
                    if len(prod) == 0:
                        if EPS not in FIRST[A]:
                            FIRST[A].add(EPS); changed = True
                        continue
                    add_epsilon = True
                    for sym in prod: # para cada símbolo na produção. Ex: sym = '(' ou 'RPN_SEQ'
                        if sym == EPS:
                            if EPS not in FIRST[A]:
                                FIRST[A].add(EPS); changed = True
                            add_epsilon = False; break
                        if not is_nonterminal(sym, G):
                            if sym not in FIRST[A]:
                                FIRST[A].add(sym); changed = True
                            add_epsilon = False; break
                        else:
                            before = len(FIRST[A])
                            FIRST[A].update(x for x in FIRST[sym] if x != EPS)
                            if len(FIRST[A]) != before: changed = True
                            if EPS in FIRST[sym]:
                                add_epsilon = True
                            else:
                                add_epsilon = False; break
                    if add_epsilon:
                        if EPS not in FIRST[A]:
                            FIRST[A].add(EPS); changed = True
        return FIRST

    def first_of_sequence(seq, FIRST, G):
        result = set()
        if len(seq) == 0:
            result.add(EPS); 
            return result
        add_epsilon = True
        for sym in seq:
            if sym == EPS:
                result.add(EPS); add_epsilon = False; break
            if not is_nonterminal(sym, G):
                result.add(sym); add_epsilon = False; break
            else:
                result.update(x for x in FIRST[sym] if x != EPS)
                if EPS in FIRST[sym]:
                    add_epsilon = True
                else:
                    add_epsilon = False; break
        if add_epsilon: 
            result.add(EPS)
        return result

    def calcularFollow(G, FIRST, start='LINHA'):
        FOLLOW = {A: set() for A in G} # inicializa FOLLOW para cada não-terminal com conjuntos vazios
        FOLLOW[start].add('$')
        changed = True
        while changed:
            changed = False
            for A in G: # para cada não-terminal A. Ex: G['EXPR']
                for prod in G[A]: # para cada produção de A. Ex = [['(', 'RPN_SEQ', ')']]
                    for i, B in enumerate(prod): # para cada símbolo na produção. Ex: B = '(' ou 'RPN_SEQ'
                        if not is_nonterminal(B, G): continue
                        beta = prod[i+1:] # tudo depois de B atual
                        first_beta = first_of_sequence(beta, FIRST, G)
                        before = len(FOLLOW[B])
                        FOLLOW[B].update(x for x in first_beta if x != EPS)
                        if EPS in first_beta or len(beta) == 0:
                            FOLLOW[B].update(FOLLOW[A])
                        if len(FOLLOW[B]) != before: changed = True
        return FOLLOW

    def construirTabelaLL1(G, FIRST, FOLLOW):
        table = {}
        conflicts = []
        for A in G: # para cada não-terminal A. Ex: G['EXPR']
            for prod in G[A]: # para cada produção de A. Ex = [['(', 'RPN_SEQ', ')']]
                first_prod = first_of_sequence(prod, FIRST, G)
                for a in (first_prod - {EPS}): # para cada terminal em FIRST(produção)
                    key = (A, a) # chave da tabela LL(1)
                    if key in table and table[key] != prod:
                        conflicts.append((key, table[key], prod))
                    else:
                        table[key] = prod
                if EPS in first_prod:
                    for b in FOLLOW[A]:
                        key = (A, b)
                        if key in table and table[key] != prod: # já existe outra produção para (A, b)
                            conflicts.append((key, table[key], prod))
                        else:
                            table[key] = prod
        return table, conflicts

    G = {} # construção da gramática usando dicionário
    G['LINHA'] = [['EXPR']] # não-terminal é chave, terminal é valor
    G['EXPR'] = [['(', 'RPN_SEQ', ')']]
    G['RPN_SEQ'] = [['TOKEN', 'RPN_TAIL']]
    G['RPN_TAIL'] = [['TOKEN', 'RPN_TAIL'], [EPS]]
    # TOKEN agora não inclui COMANDO separado; comandos são sequences de tokens:
    G['TOKEN'] = [['NUMERO'], ['IDENT'], ['OPERADOR'], ['EXPR'], ['res']]
    G['NUMERO'] = [['real']]
    G['IDENT'] = [['ident']]
    G['OPERADOR'] = [['+'], ['-'], ['*'], ['/'], ['%'], ['^'], ['|']]

    FIRST = calcularFirst(G)
    FOLLOW = calcularFollow(G, FIRST, start='LINHA')
    tabelaLL1, conflitos = construirTabelaLL1(G, FIRST, FOLLOW)

    if conflitos:
        print("Conflitos encontrados na tabela LL(1):")
        for (A, a), prod1, prod2 in conflitos:
            print(f"  Não determinismo para ({A}, {a}): {prod1} e {prod2}")
        raise ValueError("Gramática não é LL(1) devido a conflitos na tabela.")
    else:
        print("Gramática é LL(1).")
        return G, FIRST, FOLLOW, tabelaLL1

def parsear(tokens, tabelaLL1): # entrada: vetor de tokens, tabelaLL1
    stack = ['$', 'LINHA'] # pilha inicial com símbolo de início e marcador de fim
    derivation = [] # para armazenar a sequência de derivações
    index = 0 # índice para rastrear a posição atual nos tokens   
    nonterminals = {A for (A, _) in tabelaLL1.keys()} 

    def is_nonterminal(sym):
        return sym in nonterminals # true se sym é um não-terminal em G, false é terminal

    while stack:
        top = stack.pop() # obtém o símbolo do topo da pilha
        if index < len(tokens):
            current_token = tokens[index] # token atual a ser processado
        else:
            current_token = '$' # marcador de fim de entrada
        
        if top == current_token == '$':
            return derivation # análise sintática bem-sucedida
        
        if not is_nonterminal(top): # se o topo é um terminal
            if top == current_token: # se coincidem, consome o token
                index += 1
            else:
                raise ValueError(f"Erro de sintaxe: esperado '{top}', encontrado '{current_token}'")
        else: # topo é um não-terminal
            key = (top, current_token)
            if key in tabelaLL1:
                production = tabelaLL1[key]
                derivation.append((top, production)) # registra a produção usada
                for sym in reversed(production): # empilha a produção na ordem inversa
                    if sym != EPS: # não empilha epsilon
                        stack.append(sym)
            else:
                raise ValueError(f"Erro de sintaxe: não há produção para {top}, '{current_token}'")
    raise ValueError("Erro de sintaxe: pilha vazia antes do fim dos tokens")

def lerTokens(linha):
    """
    Recebe uma linha (string) e converte em lista de tokens.
    Converte números para 'real', palavras para 'ident' (exceto RES),
    e preserva operadores/parênteses.
    Se encontrar erro léxico, lança ValueError.
    """
    tokens = []
    token = ""
    parenteses = 0
    i = 0

    while i < len(linha):
        char = linha[i]

        if char.isspace():  # espaço separa tokens
            if token:
                tokens.append(token)
                token = ""
        elif char in "()":  # parênteses
            if token:
                tokens.append(token)
                token = ""
            tokens.append(char)
            if char == "(":
                parenteses += 1
            else:
                parenteses -= 1
                if parenteses < 0:
                    raise ValueError("Parêntese fechado sem correspondente.")
        elif char in "+-*/%^|":  # operadores
            if token:
                tokens.append(token)
                token = ""
            tokens.append(char)
        else:  # acumula letras/números
            token += char
        i += 1

    if token:
        tokens.append(token)

    if parenteses != 0:
        raise ValueError("Parênteses desbalanceados.")

    # converte para tokens da gramática
    final_tokens = []
    for t in tokens:
        if t.replace('.', '', 1).isdigit():  # número real (aceita um '.')
            if t.count('.') <= 1:
                final_tokens.append('real')
            else:
                raise ValueError(f"Número inválido: {t}")
        elif t.lower() == "res":
            final_tokens.append("res")
        elif t.isalpha():
            final_tokens.append("ident")
        elif t in "()*/%+^-|":
            final_tokens.append(t)
        else:
            raise ValueError(f"Token inválido: {t}")

    return final_tokens


def gerarArvore(derivacaoParser):
    pass # saída: árvore no formato estruturado

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py <nome_do_arquivo>")
    else:
        caminho = sys.argv[1]
        G, FIRST, FOLLOW, tabelaLL1 = construirGramatica()

        with open(caminho, "r", encoding="utf-8") as f:
            for numero_linha, linha in enumerate(f, start=1):
                linha = linha.strip()
                if not linha:
                    continue

                print(f"\nLinha {numero_linha}: {linha}")
                try:
                    tokens = lerTokens(linha)
                    print("Tokens lidos:", tokens)
                    derivacao = parsear(tokens, tabelaLL1)
                    print("Derivação:")
                    for step in derivacao:
                        print(f"{step[0]} -> {' '.join(step[1])}")
                except Exception as e:
                    print(f"Erro na linha {numero_linha}: {e}")
                    continue

"""if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py <nome_do_arquivo>")

    else:
        caminho = sys.argv[1]
        linhas = []
        tokens = []
        G, FIRST, FOLLOW, tabelaLL1 = construirGramatica() # contruindo a gramática e tabelas
        #lerArquivo(caminho, linhas) # implementar lerArquivo
        tokens = lerTokens(caminho) # lendo tokens do arquivo
        print("Tokens lidos:", tokens)
        derivacao = parsear(tokens, tabelaLL1) # parseando os tokens
        print("Derivação:")
        for step in derivacao:
            print(f"{step[0]} -> {' '.join(step[1])}")"""