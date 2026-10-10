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
