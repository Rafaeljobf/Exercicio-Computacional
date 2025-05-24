def avaliar_porta(tipo, entradas):
    entradas_int = [int(v) for v in entradas] 
    
    if tipo == "and":
        return 1 if all(entradas_int) else 0
    elif tipo == "nand":
        return 1 if not all(entradas_int) else 0
    elif tipo == "or":
        return 1 if any(entradas_int) else 0
    elif tipo == "nor":
        return 1 if not any(entradas_int) else 0
    elif tipo == "xor":
        sum_bits = sum(entradas_int)
        return 1 if sum_bits % 2 != 0 else 0
    elif tipo == "nxor":
        sum_bits = sum(entradas_int)
        return 1 if sum_bits % 2 == 0 else 0
    elif tipo == "not":
        return 1 if entradas_int[0] == 0 else 0
    else:
        raise ValueError(f"Tipo de porta desconhecido: {tipo}")


def gerar_tabela_verdade(circuito_definicao, defeito_fio=None, defeito_valor=None):
    entradas = circuito_definicao["entradas"]
    saidas = circuito_definicao["saidas"]
    gates = circuito_definicao["gates"]

    num_entradas = len(entradas)
    total_linhas = 2 ** num_entradas
    linhas_saida = []

    cabecalho = " ".join(entradas + saidas)
    linhas_saida.append(cabecalho)

    for i in range(total_linhas):
        valores_fios = {}

        bits_entrada = [(i >> j) & 1 for j in reversed(range(num_entradas))]
        for idx, nome_entrada in enumerate(entradas):
            valores_fios[nome_entrada] = bits_entrada[idx]

        if defeito_fio and defeito_fio in entradas:
            valores_fios[defeito_fio] = defeito_valor

        ordered_gates = []
        resolved_wires = set(entradas)
        
        while len(ordered_gates) < len(gates):
            found_ready_gate = False
            for g_name in gates:
                if g_name not in [og[0] for og in ordered_gates]:
                    gate_info = circuito_definicao[g_name]
                    entradas_gate = gate_info[2:]
                    
                    all_inputs_resolved = True
                    for input_wire in entradas_gate:
                        if input_wire not in resolved_wires:
                            all_inputs_resolved = False
                            break
                    
                    if all_inputs_resolved:
                        ordered_gates.append((g_name, gate_info))
                        resolved_wires.add(gate_info[1])
                        found_ready_gate = True
            if not found_ready_gate and len(ordered_gates) < len(gates):
                break 

        for g_name, gate_info in ordered_gates:
            tipo, saida_fio, *entradas_gate = gate_info
            
            entradas_logicas = []
            for nome_entrada_gate in entradas_gate:
                if defeito_fio and nome_entrada_gate == defeito_fio:
                    entradas_logicas.append(defeito_valor)
                else:
                    entradas_logicas.append(valores_fios[nome_entrada_gate])

            resultado_porta = avaliar_porta(tipo, entradas_logicas)
            valores_fios[saida_fio] = resultado_porta
            
            if defeito_fio and saida_fio == defeito_fio:
                valores_fios[saida_fio] = defeito_valor

        linha_completa = []
        for e in entradas:
            linha_completa.append(valores_fios[e])
        for s in saidas:
            if defeito_fio and s == defeito_fio:
                linha_completa.append(defeito_valor)
            else:
                linha_completa.append(valores_fios[s])
                
        linhas_saida.append(" ".join(map(str, linha_completa)))

    return linhas_saida


def comparar_e_gerar_diagnostico(tabela_sadia, tabela_com_defeito, nome_defeito, nome_saida_arquivo):
    diferencas_encontradas = False
    with open(nome_saida_arquivo, "a") as f_out:
        f_out.write(f"\n--- Simulaçao de Defeito: {nome_defeito} ---\n")
        f_out.write("Tabela Verdade Resultante:\n")
        
        for i in range(len(tabela_com_defeito)):
            f_out.write(tabela_com_defeito[i] + "\n")

        diferencas_linhas_indices = []
        for i in range(1, len(tabela_sadia)): 
            if tabela_sadia[i] != tabela_com_defeito[i]:
                diferencas_linhas_indices.append(i)
                diferencas_encontradas = True
        
        if diferencas_encontradas:
            f_out.write(f"Diferenças com Tabela Ideal nas linhas (considerando cabeçalho como linha 0): {', '.join(map(str, diferencas_linhas_indices))}\n")
            f_out.write("Detalhes das diferenças:\n")
            for idx in diferencas_linhas_indices:
                f_out.write(f"  Linha {idx}: Ideal -> {tabela_sadia[idx]} | Com Defeito -> {tabela_com_defeito[idx]}\n")
        else:
            f_out.write("Nenhuma diferença detectada.\n")
    
    return diferencas_encontradas


if __name__ == "__main__":
    nome_arquivo_circuito = "circuito_sadio.txt"
    nome_arquivo_diagnostico = "diagnostico.txt"

    with open(nome_arquivo_diagnostico, "w") as f_clear:
        f_clear.write("--- Relatorio de Diagnostico de Defeitos em Circuito Combinacional ---\n\n")

    with open(nome_arquivo_circuito, "r") as f:
        circuito_str = f.read().strip()
        if circuito_str.startswith(""):
            circuito_str = circuito_str[len(""):]
        circuito_sadio = eval(circuito_str)

    tabela_sadia = gerar_tabela_verdade(circuito_sadio)
    with open("saida_circuito_sadio.txt", "w") as f_sadio_out:
        for linha in tabela_sadia:
            f_sadio_out.write(linha + "\n")

    with open(nome_arquivo_diagnostico, "a") as f_out:
        f_out.write("--- Tabela Verdade Ideal (Sadia) ---\n")
        for linha in tabela_sadia:
            f_out.write(linha + "\n")
        f_out.write("\n")

    pontos_de_defeito = list(circuito_sadio['entradas'])
    for gate_name in circuito_sadio['gates']:
        output_wire = circuito_sadio[gate_name][1]
        if output_wire not in pontos_de_defeito:
            pontos_de_defeito.append(output_wire)
    
    for saida_final in circuito_sadio['saidas']:
        if saida_final not in pontos_de_defeito:
            pontos_de_defeito.append(saida_final)
    
    total_diferencas_detectadas = 0
    for ponto_fio in pontos_de_defeito:
        tabela_sa0 = gerar_tabela_verdade(circuito_sadio, defeito_fio=ponto_fio, defeito_valor=0)
        if comparar_e_gerar_diagnostico(tabela_sadia, tabela_sa0, f"Fio '{ponto_fio}' Stuck-at-0 (SA0)", nome_arquivo_diagnostico):
            total_diferencas_detectadas += 1

        tabela_sa1 = gerar_tabela_verdade(circuito_sadio, defeito_fio=ponto_fio, defeito_valor=1)
        if comparar_e_gerar_diagnostico(tabela_sadia, tabela_sa1, f"Fio '{ponto_fio}' Stuck-at-1 (SA1)", nome_arquivo_diagnostico):
            total_diferencas_detectadas += 1

    with open(nome_arquivo_diagnostico, "a") as f_out:
        f_out.write("\n--- Resumo ---\n")
        f_out.write(f"Processamento concluido. Verifique o arquivo '{nome_arquivo_diagnostico}'.\n")
        f_out.write(f"Total de simulaçoes de defeitos que causaram alguma diferença: {total_diferencas_detectadas}\n")