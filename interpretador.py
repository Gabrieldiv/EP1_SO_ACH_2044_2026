from bcp import BCP

def executar_quantum(bcp: BCP, quantum: int) -> tuple[int,str]:
    executadas = 0
    while executadas < quantum:
        instrucao = bcp.texto[bcp.pc].strip()
        bcp.pc += 1
        executadas += 1

        if instrucao == "E/S":
            return executadas, "ES"
        if instrucao == "SAIDA":
            return executadas, "SAIDA"
        if instrucao.startswith("X="):
            bcp.x = int(instrucao[2:])
        elif instrucao.startswith("Y="):
            bcp.y = int(instrucao[2:])
        # COM: não altera nada, só conta

    return executadas, "QUANTUM"