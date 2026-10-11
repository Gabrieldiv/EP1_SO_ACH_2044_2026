import os
import re
import sys

PADRAO_CARREGANDO = re.compile(r"Carregando (\S+)")
PADRAO_EXECUTANDO = re.compile(r"Executando (\S+)")
PADRAO_ES = re.compile(r"E/S iniciada em (\S+)")
PADRAO_INTERROMPENDO = re.compile(r"Interrompendo (\S+) após (\d+) instruç(?:ão|ões)")
PADRAO_TERMINADO = re.compile(r"(\S+) terminado\. X=(-?\d+)\. Y=(-?\d+)")
PADRAO_MEDIA_TROCAS = re.compile(r"MEDIA DE TROCAS: (\d+(?:\.\d+)?)")
PADRAO_MEDIA_INST = re.compile(r"MEDIA DE INSTRUCOES: (\d+(?:\.\d+)?)")
PADRAO_QUANTUM = re.compile(r"QUANTUM: (\d+)")


def ler_programas(pasta):
    programas = {}

    for arquivo in sorted(os.listdir(pasta)):
        if not arquivo.endswith(".txt") or not arquivo[:-4].isdigit():
            continue

        caminho = os.path.join(pasta, arquivo)

        with open(caminho, encoding="utf-8") as f:
            linhas = []
            for linha in f:
                linha = linha.strip()
                if linha:
                    linhas.append(linha)

        if not linhas:
            continue

        nome = linhas[0]
        instrucoes = linhas[1:]
        x = 0
        y = 0

        for comando in instrucoes:
            if comando.startswith("X="):
                x = int(comando[2:])
            elif comando.startswith("Y="):
                y = int(comando[2:])

        programas[nome] = {
            "qtd_instrucoes": len(instrucoes),
            "x_esperado": x,
            "y_esperado": y
        }

    return programas


def validar_log(caminho_log, pasta_programas):
    erros = []

    if not os.path.isdir(pasta_programas):
        return [f"Erro: pasta '{pasta_programas}' não encontrada."]

    try:
        programas = ler_programas(pasta_programas)

        with open(caminho_log, encoding="utf-8") as arquivo:
            linhas_log = []
            for linha in arquivo:
                linha = linha.strip()
                if linha:
                    linhas_log.append(linha)

    except (OSError, UnicodeError, ValueError) as erro:
        return [f"Erro ao ler os arquivos: {erro}"]

    if not linhas_log:
        return ["Formato: log vazio."]

    # Conferir as três linhas do rodapé.
    media_trocas = None
    media_inst = None
    quantum = None
    m_trocas = None
    m_inst = None
    m_quantum = None

    if len(linhas_log) >= 3:
        m_trocas = PADRAO_MEDIA_TROCAS.fullmatch(linhas_log[-3])
        m_inst = PADRAO_MEDIA_INST.fullmatch(linhas_log[-2])
        m_quantum = PADRAO_QUANTUM.fullmatch(linhas_log[-1])

    if m_trocas:
        media_trocas = float(m_trocas.group(1))
    else:
        erros.append("Rodapé: antepenúltima linha deveria ser 'MEDIA DE TROCAS: <número>'.")

    if m_inst:
        media_inst = float(m_inst.group(1))
    else:
        erros.append("Rodapé: penúltima linha deveria ser 'MEDIA DE INSTRUCOES: <número>'.")

    if m_quantum:
        quantum = int(m_quantum.group(1))
        if quantum <= 0:
            erros.append("Check 3: QUANTUM deve ser maior que zero.")
    else:
        erros.append("Rodapé: última linha deveria ser 'QUANTUM: <inteiro>'.")

    if m_trocas and m_inst and m_quantum:
        corpo = linhas_log[:-3]
    else:
        corpo = linhas_log

    carregados = {}
    terminados = {}
    soma_instrucoes = {}
    executando = None
    qtd_execucoes = 0
    qtd_interrupcoes = 0

    # Conferir os eventos na ordem em que aparecem.
    for numero, linha in enumerate(corpo, start=1):
        m_carr = PADRAO_CARREGANDO.fullmatch(linha)
        m_exec = PADRAO_EXECUTANDO.fullmatch(linha)
        m_es = PADRAO_ES.fullmatch(linha)
        m_int = PADRAO_INTERROMPENDO.fullmatch(linha)
        m_term = PADRAO_TERMINADO.fullmatch(linha)

        if m_carr:
            nome = m_carr.group(1)
            carregados[nome] = carregados.get(nome, 0) + 1

            if nome not in programas:
                erros.append(f"[Linha {numero}] Check 1: '{nome}' não existe na pasta de programas.")

        elif m_exec:
            nome = m_exec.group(1)
            qtd_execucoes += 1

            if carregados.get(nome, 0) == 0:
                erros.append(f"[Linha {numero}] Check 1: '{nome}' executado antes de ser carregado.")

            if executando is not None:
                erros.append(f"[Linha {numero}] Check 2: '{nome}' começou, mas '{executando}' não foi interrompido.")

            if nome in terminados:
                erros.append(f"[Linha {numero}] Check 6: '{nome}' executado depois de terminado.")

            executando = nome

        elif m_es:
            nome = m_es.group(1)

            if executando != nome:
                erros.append(f"[Linha {numero}] Check 2: E/S de '{nome}' sem estar executando.")

        elif m_int:
            nome = m_int.group(1)
            quantidade = int(m_int.group(2))
            qtd_interrupcoes += 1

            if executando != nome:
                erros.append(f"[Linha {numero}] Check 2: interrupção de '{nome}' sem estar executando.")
            else:
                executando = None

            if quantidade <= 0:
                erros.append(f"[Linha {numero}] Check 3: '{nome}' informou {quantidade} instruções; deve ser maior que zero.")

            if quantum is not None and quantidade > quantum:
                erros.append(f"[Linha {numero}] Check 3: '{nome}' executou {quantidade} instruções, acima do QUANTUM {quantum}.")

            soma_instrucoes[nome] = soma_instrucoes.get(nome, 0) + quantidade

        elif m_term:
            nome = m_term.group(1)
            x = int(m_term.group(2))
            y = int(m_term.group(3))
            terminados[nome] = terminados.get(nome, 0) + 1

            if nome in programas:
                esperado_x = programas[nome]["x_esperado"]
                esperado_y = programas[nome]["y_esperado"]

                if x != esperado_x or y != esperado_y:
                    erros.append(
                        f"[Linha {numero}] Check 5: '{nome}' terminou com X={x}, Y={y} "
                        f"(esperado X={esperado_x}, Y={esperado_y})."
                    )

        else:
            erros.append(f"[Linha {numero}] Formato: linha inválida: '{linha}'.")

    if executando is not None:
        erros.append(f"Check 2: '{executando}' ficou sem 'Interrompendo'.")

    if qtd_execucoes != qtd_interrupcoes:
        erros.append(
            f"Check 2: {qtd_execucoes} 'Executando' e "
            f"{qtd_interrupcoes} 'Interrompendo'; deveriam ser iguais."
        )

    # Check 1: cada processo carregado e terminado uma vez.
    nomes = set(programas) | set(carregados) | set(terminados)

    for nome in sorted(nomes):
        if carregados.get(nome, 0) != 1:
            erros.append(f"Check 1: '{nome}' carregado {carregados.get(nome, 0)} vez(es).")

        if terminados.get(nome, 0) != 1:
            erros.append(f"Check 1: '{nome}' terminado {terminados.get(nome, 0)} vez(es).")

    # Check 4: contar somente as instruções registradas no log.
    for nome in programas:
        esperado = programas[nome]["qtd_instrucoes"]
        encontrado = soma_instrucoes.get(nome, 0)

        if encontrado != esperado:
            erros.append(f"Check 4: '{nome}' soma {encontrado} instruções, mas o arquivo tem {esperado}.")

    # Conferir os valores das médias.
    if media_trocas is not None and programas:
        calculada = qtd_interrupcoes / len(programas)

        if float(f"{calculada:.2f}") != media_trocas:
            erros.append(f"Rodapé: MEDIA DE TROCAS {media_trocas}; calculada: {calculada:.2f}.")

    if media_inst is not None and qtd_interrupcoes > 0:
        calculada = sum(soma_instrucoes.values()) / qtd_interrupcoes

        if float(f"{calculada:.2f}") != media_inst:
            erros.append(f"Rodapé: MEDIA DE INSTRUCOES {media_inst}; calculada: {calculada:.2f}.")

    return erros


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python validar_log.py logs/log03.txt")
        sys.exit(1)

    pasta_programas = os.path.join(os.path.dirname(os.path.abspath(__file__)), "programas")
    erros = validar_log(sys.argv[1], pasta_programas)

    if erros:
        for erro in erros:
            print(erro)
        sys.exit(1)

    print("OK")
