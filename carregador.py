"""Carregador: lê os arquivos de entrada e cria os BCPs.

Lê os programas da pasta indicada (01.txt, 02.txt, ...), as prioridades de
prioridades.txt e o quantum de quantum.txt. Não escalona nada: só prepara os
processos para o escalonador.
"""

import os

from bcp import BCP


def carregar_programa(caminho, prioridade):
    """Lê um arquivo de programa e devolve o BCP correspondente.

    A primeira linha do arquivo é o nome do programa e as demais são as
    instruções (segmento de texto), terminando em SAIDA. O processo começa com
    tantos créditos quanto a sua prioridade (passo 1 do algoritmo).
    """
    with open(caminho, encoding="utf-8") as arquivo:
        linhas = arquivo.read().splitlines()
    inicio = linhas[0]  # nome do programa, por exemplo "TESTE-1"
    processo = BCP(inicio, linhas[1:], prioridade, creditos=prioridade)
    return processo


def carregar_programas(pasta):
    """Carrega todos os programas de uma pasta.

    Devolve a lista de BCPs (na ordem dos arquivos) e o valor do quantum lido
    de quantum.txt. A prioridade de cada processo é a linha de prioridades.txt
    que corresponde à posição do seu arquivo em ordem alfabética: 01.txt usa a
    linha 1, 02.txt a linha 2, e assim por diante.
    """
    caminho_prioridades = os.path.join(pasta, "prioridades.txt")
    with open(caminho_prioridades, encoding="utf-8") as arquivo_aux:
        linhas = arquivo_aux.read().splitlines()
    prioridades = [int(n) for n in linhas]
    nomes = sorted(os.listdir(pasta))  # ordem alfabética = ordem numérica (01, 02...)
    # Só os arquivos de programa: o nome sem ".txt" é um número (ignora, por
    # exemplo, prioridades.txt e quantum.txt)
    arquivos = [arquivo for arquivo in nomes if arquivo[:-4].isdigit()]
    processos = []
    for i, nome in enumerate(arquivos):
        # o i-ésimo programa usa a i-ésima prioridade
        processo = carregar_programa(os.path.join(pasta, nome), prioridades[i])
        processos.append(processo)

    # O quantum é um único inteiro, em quantum.txt
    with open(os.path.join(pasta, "quantum.txt"), encoding="utf-8") as arquivo_aux:
        quantum = int(arquivo_aux.read().strip())

    return processos, quantum
