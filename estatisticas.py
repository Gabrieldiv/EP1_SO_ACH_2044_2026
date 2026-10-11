"""Estatísticas do escalonador: contadores e médias exibidas no rodapé do log.

Definições do enunciado (seção 1.2):
- Média de trocas: total de vezes que cada processo foi interrompido (incluindo
  a última, em que rodou SAIDA), dividido pelo número de processos.
- Média de instruções: instruções executadas por surto de CPU, em média sobre
  todos os surtos de todos os processos.
"""


class Estatisticas:
    """Acumula o número de interrupções e o de instruções executadas.

    Uma "interrupção" (troca) é o fim de um surto de CPU, seja por fim do
    quantum, por E/S ou por SAIDA. As três contam do mesmo jeito.
    """

    def __init__(self):
        self.trocas = 0  # total de interrupções, somando todos os processos
        self.instrucoes = 0  # total de instruções executadas, todas as interrupções

    def registrar(self, n):
        """Registra um surto de CPU que terminou após executar `n` instruções.

        A E/S e a SAIDA já vêm contadas dentro de `n`, como o enunciado pede.
        """
        self.trocas += 1
        self.instrucoes += n

    def media_trocas(self, n_processos):
        """Média de trocas por processo: total de interrupções / nº de processos."""
        return self.trocas / n_processos

    def media_instrucoes(self):
        """Média de instruções por quantum: total de instruções / total de trocas."""
        return self.instrucoes / self.trocas
