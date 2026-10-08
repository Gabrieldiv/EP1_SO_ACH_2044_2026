from dataclasses import dataclass

# Estados possíveis de um processo
PRONTO = "PRONTO"
EXECUTANDO = "EXECUTANDO"
BLOQUEADO = "BLOQUEADO"

# Quantos quanta de outros processos um processo espera após uma E/S
ESPERA_ES = 2


@dataclass
class BCP:
    """Bloco de Controle de Processo."""

    nome: str  # nome do programa (1ª linha do arquivo)
    texto: list[str]  # segmento de texto: comandos do programa, terminando em SAIDA
    prioridade: int  # prioridade lida de prioridades.txt
    pc: int = 0  # contador de programa: índice da próxima instrução em texto
    estado: str = PRONTO  # PRONTO, EXECUTANDO ou BLOQUEADO
    creditos: int = 0  # créditos atuais (o carregador coloca a prioridade aqui)
    x: int = 0  # registrador X
    y: int = 0  # registrador Y
    espera: int = 0  # quanta que faltam para sair do bloqueio de E/S
