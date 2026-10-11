"""Bloco de Controle de Processo (BCP) e constantes de estado.

Este módulo define a estrutura que representa um processo dentro do escalonador.
O BCP guarda tudo o que é necessário para que um processo, depois de interrompido,
possa voltar a rodar exatamente de onde parou.
"""

from dataclasses import dataclass

# Estados possíveis de um processo
PRONTO = "PRONTO"  # esperando na lista de prontos para ganhar a CPU
EXECUTANDO = "EXECUTANDO"  # é o processo que está rodando no momento
BLOQUEADO = "BLOQUEADO"  # esperando o fim de uma E/S, na lista de bloqueados

# Quantos quanta de outros processos um processo espera após uma E/S
ESPERA_ES = 2


@dataclass
class BCP:
    """Bloco de Controle de Processo.

    Cada processo carregado tem um BCP. A Tabela de Processos, a lista de prontos
    e a lista de bloqueados guardam referências a esses objetos (o mesmo BCP
    aparece em mais de uma lista, mas nunca é copiado).
    """

    nome: str  # nome do programa (1ª linha do arquivo)
    texto: list[str]  # segmento de texto: comandos do programa, terminando em SAIDA
    prioridade: int  # prioridade lida de prioridades.txt (fixa durante a execução)
    pc: int = 0  # contador de programa: índice da próxima instrução em texto
    estado: str = PRONTO  # PRONTO, EXECUTANDO ou BLOQUEADO
    creditos: int = 0  # créditos atuais (o carregador coloca a prioridade aqui)
    x: int = 0  # registrador X (começa em 0)
    y: int = 0  # registrador Y (começa em 0)
    espera: int = 0  # quanta que faltam para sair do bloqueio de E/S
