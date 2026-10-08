from bcp import BCP 

def carregar_programa(caminho):
    linhas = open(caminho, encoding = "utf-8").read().splitlines()
    inicio = linhas[0]
    processo = BCP(inicio,linhas[1:],1)
    return processo