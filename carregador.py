import os
from bcp import BCP 

def carregar_programa(caminho, prioridade):
    linhas = open(caminho, encoding = "utf-8").read().splitlines()
    inicio = linhas[0]
    processo = BCP(inicio,linhas[1:],prioridade, creditos=prioridade)
    return processo


def carregar_programas(pasta):
    caminho_prioridades = os.path.join(pasta,"prioridades.txt")
    linhas = open(caminho_prioridades, encoding = "utf-8").read().splitlines()
    prioridades = [int(n) for n in linhas]
    nomes = sorted(os.listdir(pasta))
    arquivos = [arquivo for arquivo in nomes if arquivo[:-4].isdigit()]
    processos = []
    for i, nome in enumerate(arquivos):
        processo = carregar_programa(os.path.join(pasta, nome), prioridades[i])
        processos.append(processo)

    quantum = int(open(os.path.join(pasta, "quantum.txt"), encoding="utf-8").read().strip())

    return processos, quantum