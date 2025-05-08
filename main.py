def avaliar_porta(tipo, entradas):
    if tipo == "and":
        return all(entradas)  # Aceita 2 ou mais entradas
    elif tipo == "nand":
        return not all(entradas)
    elif tipo == "or":
        return any(entradas)
    elif tipo == "nor":
        return not any(entradas)
    elif tipo == "xor":
        result = False
        for v in entradas:
            result ^= v
        return result
    elif tipo == "nxor":
        result = False
        for v in entradas:
            result ^= v
        return not result
    elif tipo == "not":
        return not entradas[0]
    
def comparar_tabelas_e_salvar(tabela_sadia, tabela_defeituosa, nome_saida):
    diferencas = []

    with open(nome_saida, "w") as f_out:
        f_out.write("Linhas com defeitos detectados:\n")
        f_out.write("-" * 40 + "\n")

        for linha_s, linha_d in zip(tabela_sadia[1:], tabela_defeituosa[1:]):  # Ignora o cabeçalho
            if linha_s != linha_d:
                diferencas.append((linha_s, linha_d))
                f_out.write(f"Sadio: {linha_s}\nDefeituoso: {linha_d}\n")
                f_out.write("-" * 30 + "\n")

    print(f"Diagnóstico gerado em '{nome_saida}'.")

    return diferencas

def gerar_tabela_verdade(nome_entrada, nome_saida):
    with open(nome_entrada, "r") as f:
        circuito = eval(f.read())

    entradas = circuito["entradas"]
    saidas = circuito["saidas"]
    gates = circuito["gates"]

    n = len(entradas)
    total_linhas = 2 ** n
    linhas_saida = []

    # Cabeçalho tabela verdade
    cabecalho = " ".join(entradas + saidas)
    linhas_saida.append(cabecalho)

    # Para cada combinação de entradas
    for i in range(total_linhas):
        valores = {}
        bits = [(i >> j) & 1 for j in reversed(range(n))]
        for idx, nome in enumerate(entradas):
            valores[nome] = bool(bits[idx])

        # Avaliação das portas lógicas (gates)
        for g in gates:
            tipo, saida, *entradas_gate = circuito[g]
            entradas_logicas = [valores[nome] for nome in entradas_gate]
            valores[saida] = avaliar_porta(tipo, entradas_logicas)

        # Linha da tabela
        linha = [int(valores[e]) for e in entradas + saidas]
        linhas_saida.append(" ".join(map(str, linha)))

    # Escreve no arquivo de saída
    with open(nome_saida, "w") as f_out:
        for linha in linhas_saida:
            f_out.write(linha + "\n")

    print(f"Tabela verdade salva com sucesso em '{nome_saida}'.")

    return linhas_saida  
    
# Gera tabela verdade para os circuitos sadio e defeituoso
tabela_sadia = gerar_tabela_verdade("circuito_sadio.txt", "saida_circuito_sadio.txt")
tabela_defeituosa = gerar_tabela_verdade("circuito_defeituoso.txt", "saida_circuito_defeituoso.txt")

diferencas = comparar_tabelas_e_salvar(tabela_sadia, tabela_defeituosa, 'diagnostico.txt')  

print("Linhas com defeitos detectados:")
for sadio, defeituoso in diferencas:
    print(f"Sadio: {sadio} | Defeituoso: {defeituoso}")
