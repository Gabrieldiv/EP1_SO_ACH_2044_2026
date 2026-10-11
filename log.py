"""Logfile do escalonador, no formato exigido pelo enunciado (seção 1.2).

Cada método escreve uma linha de evento. As mensagens seguem o texto do
enunciado, sem acentos nos rodapés, e o arquivo usa quebra de linha "\\n".
"""


class Log:
    """Escreve o logfile (logNN.txt) enquanto o escalonador roda.

    O arquivo é aberto ao criar o objeto e fica aberto até `fechar()`.
    """

    def __init__(self, caminho):
        # Modo "w" recria o arquivo a cada execução. newline="\n" garante a mesma
        # quebra de linha em qualquer sistema (inclusive Windows).
        # O arquivo é aberto de propósito sem `with`, pois é usado por toda a
        # simulação e fechado em `fechar()`; por isso o noqa do ruff.
        self.arquivo = open(caminho, "w", encoding="utf-8", newline="\n")  # noqa: SIM115

    def carregando(self, nome):
        """Registra um processo carregado (um por linha, na ordem da fila de prontos)."""
        self.arquivo.write(f"Carregando {nome}\n")

    def executando(self, nome):
        """Registra o processo que passa a executar."""
        self.arquivo.write(f"Executando {nome}\n")

    def es_iniciada(self, nome):
        """Registra o início de uma E/S (vem antes da linha "Interrompendo")."""
        self.arquivo.write(f"E/S iniciada em {nome}\n")

    def fechar(self):
        """Fecha o arquivo. Deve ser chamado depois do rodapé."""
        self.arquivo.close()

    def interrompendo(self, nome, n):
        """Registra a interrupção do processo após `n` instruções do último surto."""
        # "instrução" no singular quando n == 1, como no exemplo do enunciado
        palavra = "instrução" if n == 1 else "instruções"
        self.arquivo.write(f"Interrompendo {nome} após {n} {palavra}\n")

    def terminado(self, nome, x, y):
        """Registra o fim de um processo, com o valor final de X e Y."""
        self.arquivo.write(f"{nome} terminado. X={x}. Y={y}\n")

    def rodape(self, media_trocas, media_instrucoes, quantum):
        """Escreve as três linhas finais: médias (2 casas decimais) e o quantum."""
        self.arquivo.write(f"MEDIA DE TROCAS: {media_trocas:.2f}\n")
        self.arquivo.write(f"MEDIA DE INSTRUCOES: {media_instrucoes:.2f}\n")
        # Última linha sem "\n" no final, como nos logs já validados
        self.arquivo.write(f"QUANTUM: {quantum}")
