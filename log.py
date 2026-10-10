class Log:
    def __init__(self, caminho):
        self.arquivo = open(caminho, "w", encoding="utf-8", newline="\n")  # noqa: SIM115

    def carregando(self, nome):
        self.arquivo.write(f"Carregando {nome}\n")

    def executando(self, nome):
        self.arquivo.write(f"Executando {nome}\n")

    def es_iniciada(self, nome):
        self.arquivo.write(f"E/S iniciada em {nome}\n")

    def fechar(self):
        self.arquivo.close()

    def interrompendo(self, nome, n):
        palavra = "instrução" if n == 1 else "instruções"
        self.arquivo.write(f"Interrompendo {nome} após {n} {palavra}\n")

    def terminado(self, nome, x, y):
        self.arquivo.write(f"{nome} terminado. X={x}. Y={y}\n")

    def rodape(self, media_trocas, media_instrucoes, quantum):
        self.arquivo.write(f"MEDIA DE TROCAS: {media_trocas:.2f}\n")
        self.arquivo.write(f"MEDIA DE INSTRUCOES: {media_instrucoes:.2f}\n")
        self.arquivo.write(f"QUANTUM: {quantum}")
