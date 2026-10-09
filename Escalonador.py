import argparse
import os

from bcp import BLOQUEADO, ESPERA_ES, EXECUTANDO, PRONTO
from carregador import carregar_programas
from interpretador import executar_quantum


def desbloquear(processos, bloqueados):
    for b in bloqueados[:]:
        b.espera -= 1
        if b.espera == 0:
            b.estado = PRONTO
            processos.append(b)
            bloqueados.remove(b)


def escalonar(pasta, quantum_usuario=None, saida="logs"):
    processos, quantum = carregar_programas(pasta)
    if quantum_usuario is not None:
        quantum = quantum_usuario

    bloqueados = []
    processos.sort(key=lambda p: p.creditos, reverse=True)

    for p in processos:
        print(p.nome)

    trocas = 0
    instrucoes = 0
    n_processos = len(processos)

    while processos or bloqueados:
        vivos = processos + bloqueados
        if all(p.creditos == 0 for p in vivos):
            for p in vivos:
                p.creditos = p.prioridade

        if not processos:
            desbloquear(processos, bloqueados)
            continue

        processos.sort(key=lambda p: p.creditos, reverse=True)
        atual = processos.pop(0)
        atual.estado = EXECUTANDO
        atual.creditos = max(0, atual.creditos - 1)
        print()
        print(atual.nome, atual.creditos)
        n, motivo = executar_quantum(atual, quantum)
        trocas += 1
        instrucoes += n
        desbloquear(processos, bloqueados)

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
        print(trocas, instrucoes)
    media_trocas = trocas / n_processos
    media_instrucoes = instrucoes / trocas

    print(f"{media_trocas:.2f}")
    print(f"{media_instrucoes:.2f}")
    print(len(bloqueados))

    os.makedirs(saida, exist_ok=True)
    caminho = os.path.join(saida, f"log{quantum:02d}.txt")
    with open(caminho, mode="w", encoding="utf-8") as f:
        f.write(
            f"MEDIA DE TROCAS: {media_trocas:.2f}\n"
            f"MEDIA DE INSTRUCOES: {media_instrucoes:.2f}\n"
            f"QUANTUM: {quantum}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quantum", type=int)
    parser.add_argument("--programas", default="programas")
    parser.add_argument("--saida", default="logs")
    args = parser.parse_args()
    escalonar(args.programas, args.quantum, args.saida)
