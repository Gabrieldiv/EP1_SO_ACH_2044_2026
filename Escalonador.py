"""Escalonador de processos (ponto de entrada do sistema).

Simula um escalonador de prioridades por créditos para uma máquina com um único
processador. Contém as estruturas centrais exigidas pelo enunciado: a Tabela de
Processos, a lista de prontos e a lista de bloqueados (os BCPs ficam em bcp.py).

Uso: python Escalonador.py [--quantum N] [--programas DIR] [--saida DIR]
"""

import argparse
import os
from pathlib import Path

from bcp import BLOQUEADO, ESPERA_ES, EXECUTANDO, PRONTO
from carregador import carregar_programas
from estatisticas import Estatisticas
from interpretador import executar_quantum
from log import Log

# Pasta onde está localizado Escalonador.py. Os caminhos padrão partem daqui, para
# o programa funcionar não importa de qual pasta o comando seja chamado.
BASE = Path(__file__).resolve().parent


def desbloquear(prontos, bloqueados):
    """Avança em um quantum o tempo de espera de todos os processos bloqueados.

    Os que chegam a zero terminam a E/S: passam a PRONTO e vão da lista de
    bloqueados para a lista de prontos (onde serão posicionados por créditos).
    """
    # Percorre uma cópia (bloqueados[:]) porque remove elementos da lista original
    for b in bloqueados[:]:
        b.espera -= 1
        if b.espera == 0:
            b.estado = PRONTO
            prontos.append(b)
            bloqueados.remove(b)


def escalonar(pasta, quantum_usuario=None, saida="logs"):
    """Carrega os programas de `pasta`, roda o escalonador e grava o logfile.

    Se `quantum_usuario` for dado, ele vale no lugar do quantum.txt. O log é
    gravado em `saida`/logNN.txt, em que NN é o quantum com dois dígitos.
    """
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
    # Ordenação inicial (passo 2 do algoritmo). A ordenação é estável: processos
    # com o mesmo número de créditos mantêm a ordem dos arquivos.
    prontos.sort(key=lambda p: p.creditos, reverse=True)

    # O log registra os processos carregados na ordem da fila de prontos
    for p in prontos:
        log.carregando(p.nome)

    # Guardado antes do laço, porque a tabela fica vazia no fim (média de trocas)
    n_processos = len(tabela)

    # O sistema roda até todos os processos terminarem (executarem SAIDA)
    while tabela:
        # Passo 3d: só redistribui quando TODOS os processos vivos (prontos e
        # bloqueados) têm zero crédito. Por isso olha a tabela, não só os prontos.
        if all(p.creditos == 0 for p in tabela):
            for p in tabela:
                p.creditos = p.prioridade

        # Passo 5: ninguém pronto (todos bloqueados). O tempo avança sem rodar
        # nada e sem escrever no log, até algum bloqueado voltar a pronto.
        if not prontos:
            desbloquear(prontos, bloqueados)
            continue

        # Escolhe o de mais créditos. Se a fila de prontos tem todos com zero
        # crédito mas há bloqueados com crédito, a ordenação estável faz dela
        # uma fila comum (seção 1.4 do enunciado).
        prontos.sort(key=lambda p: p.creditos, reverse=True)
        atual = prontos.pop(0)
        atual.estado = EXECUTANDO
        # Passo 3a: perde um crédito ao começar a rodar (nunca fica negativo)
        atual.creditos = max(0, atual.creditos - 1)
        log.executando(atual.nome)
        # Roda até `quantum` instruções; n = quantas rodou, motivo = por que parou
        n, motivo = executar_quantum(atual, quantum)
        estatisticas.registrar(n)
        # A E/S é registrada antes do "Interrompendo" (ordem do log do enunciado)
        if motivo == "ES":
            log.es_iniciada(atual.nome)
        log.interrompendo(atual.nome, n)
        # Um surto terminou: os que já estavam bloqueados avançam um quantum.
        # Isso é feito ANTES de colocar o processo atual na lista de bloqueados,
        # para ele esperar por dois OUTROS processos (passo 4d).
        desbloquear(prontos, bloqueados)

        # Destino do processo que acabou de rodar, conforme o motivo da parada
        if motivo == "QUANTUM":
            # Acabou o quantum: volta para prontos (será reposicionado no sort)
            atual.estado = PRONTO
            prontos.append(atual)
        elif motivo == "ES":
            # Fez E/S: vai para o fim da lista de bloqueados e espera 2 quanta
            atual.estado = BLOQUEADO
            atual.espera = ESPERA_ES
            bloqueados.append(atual)
        else:
            # Executou SAIDA: terminou, sai do sistema (passo 6)
            log.terminado(atual.nome, atual.x, atual.y)
            tabela.remove(atual)

    # Rodapé do logfile: médias e quantum usado
    media_trocas = estatisticas.media_trocas(n_processos)
    media_instrucoes = estatisticas.media_instrucoes()
    log.rodape(media_trocas, media_instrucoes, quantum)
    log.fechar()


if __name__ == "__main__":
    # Linha de comando. Sem --quantum, vale o quantum.txt da pasta de programas.
    parser = argparse.ArgumentParser()
    parser.add_argument("--quantum", type=int)
    parser.add_argument("--programas", default=str(BASE / "programas"))
    parser.add_argument("--saida", default=str(BASE / "logs"))
    args = parser.parse_args()
    escalonar(args.programas, args.quantum, args.saida)
