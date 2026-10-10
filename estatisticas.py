class Estatisticas:
    def __init__(self):
        self.trocas = 0
        self.instrucoes = 0

    def registrar(self, n):
        self.trocas += 1
        self.instrucoes += n

    def media_trocas(self, n_processos):
        return self.trocas / n_processos

    def media_instrucoes(self):
        return self.instrucoes / self.trocas
