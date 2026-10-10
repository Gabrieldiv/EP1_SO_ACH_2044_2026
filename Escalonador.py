import argparse
import os
from pathlib import Path

from bcp import BLOQUEADO, ESPERA_ES, EXECUTANDO, PRONTO
from carregador import carregar_programas
from estatisticas import Estatisticas
from interpretador import executar_quantum
from log import Log

BASE = Path(__file__).resolve().parent  # Pasta onde está localizado Escalonador.py


def desbloquear(prontos, bloqueados):
    for b in bloqueados[:]:
        b.espera -= 1
        if b.espera == 0:
            b.estado = PRONTO
            prontos.append(b)
            bloqueados.remove(b)


def escalonar(pasta, quantum_usuario=None, saida="logs"):
    # Tabela de Processos: todos os BCPs ainda vivos (sai daqui ao executar SAIDA)
    tabela, quantum = carregar_programas(pasta)
    # Lista de prontos: ordenada por créditos (maior primeiro); é uma cópia da tabela
    prontos = list(tabela)
    if quantum_usuario is not None:
        quantum = quantum_usuario
    os.makedirs(saida, exist_ok=True)
    caminho = os.path.join(saida, f"log{quantum:02d}.txt")
    log = Log(caminho)
    estatisticas = Estatisticas()

    # Lista de bloqueados: processos esperando a E/S, em ordem de chegada
    bloqueados = []
    prontos.sort(key=lambda p: p.creditos, reverse=True)

    for p in prontos:
        log.carregando(p.nome)

    n_processos = len(tabela)

    while tabela:
        if all(p.creditos == 0 for p in tabela):
            for p in tabela:
                p.creditos = p.prioridade

        if not prontos:
            desbloquear(prontos, bloqueados)
            continue

        prontos.sort(key=lambda p: p.creditos, reverse=True)
        atual = prontos.pop(0)
        atual.estado = EXECUTANDO
        atual.creditos = max(0, atual.creditos - 1)
        log.executando(atual.nome)
        n, motivo = executar_quantum(atual, quantum)
        estatisticas.registrar(n)
        if motivo == "ES":
            log.es_iniciada(atual.nome)
        log.interrompendo(atual.nome, n)
        desbloquear(prontos, bloqueados)

        if motivo == "QUANTUM":
            atual.estado = PRONTO
            prontos.append(atual)
        elif motivo == "ES":
            atual.estado = BLOQUEADO
            atual.espera = ESPERA_ES
            bloqueados.append(atual)
        else:
            log.terminado(atual.nome, atual.x, atual.y)
            tabela.remove(atual)

    media_trocas = estatisticas.media_trocas(n_processos)
    media_instrucoes = estatisticas.media_instrucoes()
    log.rodape(media_trocas, media_instrucoes, quantum)
    log.fechar()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quantum", type=int)
    parser.add_argument("--programas", default=str(BASE / "programas"))
    parser.add_argument("--saida", default=str(BASE / "logs"))
    args = parser.parse_args()
    escalonar(args.programas, args.quantum, args.saida)
