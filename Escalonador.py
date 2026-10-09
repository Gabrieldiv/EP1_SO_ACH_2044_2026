from carregador import carregar_programas
from interpretador import executar_quantum


def escalonar(pasta):
    processos, quantum = carregar_programas(pasta)

    processos.sort(key=lambda p: p.creditos, reverse=True)
    atual = processos.pop(0)
    atual.creditos = max(0, atual.creditos - 1)
    print(atual.nome, atual.creditos)
    n, motivo = executar_quantum(atual, quantum)
    print(n, motivo, atual.pc, atual.x, atual.y)


if __name__ == "__main__":
    escalonar("programas")
