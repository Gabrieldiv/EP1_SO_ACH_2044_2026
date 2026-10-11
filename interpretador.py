"""Interpretador da máquina fictícia.

Como não há clock para preemptar os processos, é o escalonador que lê e executa
cada instrução, funcionando como um interpretador. A máquina tem só 4 instruções:
atribuição (X=<valor> ou Y=<valor>), COM, E/S e SAIDA.
"""

from bcp import BCP


def executar_quantum(bcp: BCP, quantum: int) -> tuple[int, str]:
    """Executa até `quantum` instruções do processo, a partir do seu PC.

    Para antes do fim do quantum se encontrar E/S ou SAIDA. Devolve um par
    (instruções executadas, motivo da parada), em que o motivo é:
      - "QUANTUM": executou `quantum` instruções sem E/S nem SAIDA;
      - "ES": a última instrução executada foi E/S (o processo vai bloquear);
      - "SAIDA": a última instrução executada foi SAIDA (o processo terminou).
    A E/S e a SAIDA contam como instruções executadas (seção 1.4 do enunciado).
    """
    executadas = 0
    while executadas < quantum:
        instrucao = bcp.texto[bcp.pc].strip()
        # O PC avança antes de executar, então já aponta para a próxima
        # instrução. É daí que o processo recomeça depois de uma E/S.
        bcp.pc += 1
        executadas += 1

        if instrucao == "E/S":
            return executadas, "ES"
        if instrucao == "SAIDA":
            return executadas, "SAIDA"
        # Atribuição: o valor vem depois do "=" (ex.: "X=8" guarda 8 em bcp.x)
        if instrucao.startswith("X="):
            bcp.x = int(instrucao[2:])
        elif instrucao.startswith("Y="):
            bcp.y = int(instrucao[2:])
        # COM: não altera nada, só conta

    # Saiu do laço: executou o quantum inteiro sem E/S nem SAIDA
    return executadas, "QUANTUM"
