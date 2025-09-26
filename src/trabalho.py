# Integrantes do grupo:
# Ana Maria Midori Rocha Hinoshita - anamariamidori
# Lucas Antonio Linhares - Sabuti
#
# Nome do grupo no Canvas: RA2 5

import sys # import para gerenciar argumentos de linha de comando

def construirGramatica(): # nenhuma entrada, gramática fixa
    pass # saída: dados da gramática, FIRST, FOLLOW, tabelaLL1

def parsear(tokens, tabelaLL1): 
    pass # saída: estrutura de derivação para gerarArvore

def lerTokens(nomeArquivoTokens):
    pass # saída: vetor de tokens estruturado

def gerarArvore(derivacaoParser):
    pass # saída: árvore no formato estruturado

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py <nome_do_arquivo>")
    else:
        caminho = sys.argv[1]
        #lerArquivo(caminho, linhas) # implementar lerArquivo
        linhas = []
        for linha in linhas:
            tokens = []
            try:
                pass
            except ValueError as e:
                print(e)