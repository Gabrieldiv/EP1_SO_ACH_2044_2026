from bcp import BLOQUEADO, ESPERA_ES, EXECUTANDO, PRONTO
from carregador import carregar_programas
from interpretador import executar_quantum


def escalonar(pasta):
    processos, quantum = carregar_programas(pasta)

    processos.sort(key=lambda p: p.creditos, reverse=True)
    bloqueados = []
    while processos:
        atual = processos.pop(0)
        atual.estado = EXECUTANDO
        atual.creditos = max(0, atual.creditos - 1)
        print(atual.nome, atual.creditos)
        n, motivo = executar_quantum(atual, quantum)
        if motivo == "QUANTUM":
            atual.estado = PRONTO
            processos.append(atual)
        elif motivo == "ES":
            atual.estado = BLOQUEADO
            atual.espera = ESPERA_ES
            bloqueados.append(atual)
        else:
            print(f"{atual.nome} terminado. X={atual.x}. Y={atual.y}")

        print(n, motivo, atual.pc, atual.x, atual.y)
    print(len(bloqueados))


if __name__ == "__main__":
    escalonar("programas")
