import argparse
import os

from bcp import BLOQUEADO, ESPERA_ES, EXECUTANDO, PRONTO
from carregador import carregar_programas
from estatisticas import Estatisticas
from interpretador import executar_quantum
from log import Log


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
    os.makedirs(saida, exist_ok=True)
    caminho = os.path.join(saida, f"log{quantum:02d}.txt")
    log = Log(caminho)
    estatisticas = Estatisticas()

    bloqueados = []
    processos.sort(key=lambda p: p.creditos, reverse=True)

    for p in processos:
        log.carregando(p.nome)

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
        log.executando(atual.nome)
        n, motivo = executar_quantum(atual, quantum)
        estatisticas.registrar(n)
        if motivo == "ES":
            log.es_iniciada(atual.nome)
        log.interrompendo(atual.nome, n)
        desbloquear(processos, bloqueados)

        if motivo == "QUANTUM":
            atual.estado = PRONTO
            processos.append(atual)
        elif motivo == "ES":
            atual.estado = BLOQUEADO
            atual.espera = ESPERA_ES
            bloqueados.append(atual)
        else:
            log.terminado(atual.nome, atual.x, atual.y)

    media_trocas = estatisticas.media_trocas(n_processos)
    media_instrucoes = estatisticas.media_instrucoes()
    log.rodape(media_trocas, media_instrucoes, quantum)
    log.fechar()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quantum", type=int)
    parser.add_argument("--programas", default="programas")
    parser.add_argument("--saida", default="logs")
    args = parser.parse_args()
    escalonar(args.programas, args.quantum, args.saida)
