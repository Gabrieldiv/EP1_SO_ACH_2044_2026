from carregador import carregar_programas

def escalonar(pasta):
    processos, quantum = carregar_programas(pasta)

    processos.sort(key = lambda p: p.creditos, reverse=True)

    for p in processos:
        print(p.nome, p.creditos)





if __name__ == "__main__":
    escalonar("programas")
