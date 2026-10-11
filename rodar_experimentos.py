"""Experimentos: roda o escalonador para vários quanta e resume os resultados.

Para cada valor de quantum em QUANTA, executa o Escalonador, lê as três últimas
linhas do logfile gerado (média de trocas, média de instruções e quantum) e
produz, na pasta do projeto:
  - resultados.csv: tabela com os valores de todos os quanta;
  - grafico_trocas.png e grafico_instrucoes.png: um gráfico para cada média.

Uso: python rodar_experimentos.py [--sem-rodar]
     (com --sem-rodar, só lê os logs que já existem em logs/)
Requer a biblioteca matplotlib (pip install matplotlib).
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt

# Só gera arquivos de imagem, sem abrir janela (o script nunca chama plt.show())
plt.switch_backend("Agg")

BASE = Path(__file__).resolve().parent  # Pasta do projeto
QUANTA = list(range(1, 22, 2))  # 1, 3, 5, ..., 21 (21 = tamanho máximo de programa)
TIMEOUT_S = 10  # Timeout para detectar possíveis bugs no escalonador


# Execução do Escalonador
def caminho_log(pasta_logs, quantum):
    """Caminho do logfile de um quantum (logNN.txt, NN com dois dígitos)."""
    return pasta_logs / f"log{quantum:02d}.txt"


def rodar_escalonador(quantum, pasta_logs):
    """Roda o Escalonador.py com o quantum dado, como o usuário rodaria.

    Encerra o programa com mensagem de erro se o escalonador falhar ou passar do
    tempo limite (o que indicaria, por exemplo, um laço infinito).
    """
    comando = [
        sys.executable,
        "Escalonador.py",
        "--quantum",
        str(quantum),
        "--saida",
        pasta_logs,
    ]
    try:
        resultado = subprocess.run(
            comando,
            cwd=BASE,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        sys.exit(
            f"ERRO: o Escalonador passou de {TIMEOUT_S}s com quantum={quantum} (possível laço infinito)."
        )

    if resultado.returncode != 0:
        sys.exit(
            f"ERRO: o Escalonador falhou com quantum={quantum} "
            f"(código {resultado.returncode}).\n{resultado.stderr.strip()}"
        )


# Leitura dos logs
def ler_medias(caminho, quantum_esperado):
    """Lê o rodapé de um logfile e devolve (média de trocas, média de instruções).

    O rodapé tem sempre três linhas, na ordem: MEDIA DE TROCAS, MEDIA DE
    INSTRUCOES e QUANTUM. Confere se o quantum do log é o esperado.
    """
    with open(caminho, encoding="utf-8") as f:
        linhas = f.read().strip().splitlines()
    # Cada linha tem a forma "RÓTULO: valor"; pega o que vem depois dos dois pontos
    trocas = float(linhas[-3].split(":")[1])
    instrucoes = float(linhas[-2].split(":")[1])
    quantum = int(linhas[-1].split(":")[1])
    if quantum != quantum_esperado:
        sys.exit(f"Quantum errado no log: esperado {quantum_esperado}, veio {quantum}")
    return trocas, instrucoes


# Saídas: CSV e gráficos
def salvar_csv(resultados, destino):
    """Grava resultados.csv (quantum, media_trocas, media_instrucoes)."""
    caminho = destino / "resultados.csv"
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["quantum", "media_trocas", "media_instrucoes"])
        escritor.writerows(resultados)
    return caminho


def gerar_grafico(quanta, valores, titulo, rotulo_y, caminho):
    """Desenha um gráfico de linha (valor x quantum) e salva em `caminho`."""
    fig, eixo = plt.subplots(figsize=(8, 5))
    eixo.plot(quanta, valores, marker="o", linewidth=2)
    for q, v in zip(quanta, valores):  # valor escrito em cada ponto
        eixo.annotate(
            f"{v:.2f}",
            (q, v),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
        )
    eixo.set_title(titulo)
    eixo.set_xlabel("Quantum (nº de comandos)")
    eixo.set_ylabel(rotulo_y)
    eixo.set_xticks(quanta)  # um marcador para cada quantum testado
    eixo.margins(y=0.12)  # folga no topo para os rótulos
    eixo.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)  # libera a memória da figura


def gerar_graficos(resultados, destino):
    """Gera os dois gráficos pedidos: média de trocas e média de instruções."""
    quanta = [r[0] for r in resultados]
    g_trocas = destino / "grafico_trocas.png"
    g_instr = destino / "grafico_instrucoes.png"
    gerar_grafico(
        quanta,
        [r[1] for r in resultados],
        "Número médio de trocas por processo x quantum",
        "Média de trocas por processo",
        g_trocas,
    )
    gerar_grafico(
        quanta,
        [r[2] for r in resultados],
        "Média de instruções por quantum x quantum",
        "Média de instruções por quantum",
        g_instr,
    )
    return [g_trocas, g_instr]


# Programa principal
def main():
    """Roda (ou só lê) os experimentos e gera a tabela, o CSV e os gráficos."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sem-rodar",
        action="store_true",
        help="não executa o Escalonador, só lê os logs já existentes",
    )
    args = parser.parse_args()

    pasta_logs = BASE / "logs"
    destino = BASE
    if not args.sem_rodar:
        for q in QUANTA:
            print(f"Rodando Escalonador com quantum={q}...")
            rodar_escalonador(q, "logs")

    # Lê o rodapé de cada log: lista de tuplas (quantum, média trocas, média instr.)
    resultados = []
    for q in QUANTA:
        trocas, instrucoes = ler_medias(caminho_log(pasta_logs, q), q)
        resultados.append((q, trocas, instrucoes))

    arquivos = [salvar_csv(resultados, destino)] + gerar_graficos(resultados, destino)

    # Tabela impressa no terminal
    print("\nquantum  media_trocas  media_instrucoes")
    for q, t, i in resultados:
        print(f"{q:>7}  {t:>12.2f}  {i:>16.2f}")
    print("\nArquivos gerados:")
    for arquivo in arquivos:
        print(f"  {arquivo}")


if __name__ == "__main__":
    main()
