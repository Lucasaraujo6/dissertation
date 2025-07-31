import data

author = 'kinable'
instances = data.listInsts(author, log=False)

# Contadores e acumuladores
otimos_autoral = 0
otimos_kinable = 0
gap_total_autoral = 0.0
gap_total_kinable = 0.0
tempo_total_autoral = 0.0
tempo_total_kinable = 0.0
total = 0

for insNumber in range(1, instances + 1):
    i, j, k, seed = data.get_inst_parameters(insNumber, author)
    dt = data.get_data(insNumber, author)

    if None in (dt.md_authorial_1_cost, dt.md_authorial_1_best_integer,
                dt.md_kinable_homo_cost, dt.md_kinable_homo_best_integer,
                dt.md_authorial_1_time, dt.md_kinable_homo_time):
        continue

    a_cost = dt.md_authorial_1_cost
    a_ub = dt.md_authorial_1_best_integer
    k_cost = dt.md_kinable_homo_cost
    k_ub = dt.md_kinable_homo_best_integer
    a_time = dt.md_authorial_1_time
    k_time = dt.md_kinable_homo_time

    is_otimo_autoral = abs(a_cost - a_ub) < 1e-3
    is_otimo_kinable = abs(k_cost - k_ub) < 1e-3

    total += 1
    if is_otimo_autoral:
        otimos_autoral += 1
    if is_otimo_kinable:
        otimos_kinable += 1

    if a_ub > 1e-6:
        gap_total_autoral += (a_ub - a_cost) / a_ub
    if k_ub > 1e-6:
        gap_total_kinable += (k_ub - k_cost) / k_ub

    tempo_total_autoral += a_time
    tempo_total_kinable += k_time

gap_medio_autoral = 100 * gap_total_autoral / total if total > 0 else 0
gap_medio_kinable = 100 * gap_total_kinable / total if total > 0 else 0
tempo_medio_autoral = tempo_total_autoral / total if total > 0 else 0
tempo_medio_kinable = tempo_total_kinable / total if total > 0 else 0

# Tabela LaTeX com linha separada para gap e tempo médio
print("\\begin{table}[ht!]")
print("\\centering")
print("\\caption{Resumo de performance dos modelos}")
print("\\label{tab:resumo}")
print("\\begin{tabular}{lcc}")
print("\\toprule")
print("& Modelo proposto & Modelo de \\citeauthor{kinable} \\\\")
print("\\midrule")
print(f"Nº de ótimos & ${otimos_autoral}/{total}$ & ${otimos_kinable}/{total}$ \\\\")
print(f"Gap médio (\\%) & {gap_medio_autoral:.2f}\\% & {gap_medio_kinable:.2f}\\% \\\\")
print(f"Tempo médio (s) & {tempo_medio_autoral:.2f} & {tempo_medio_kinable:.2f} \\\\")
print("\\bottomrule")
print("\\end{tabular}")
print("\\end{table}")

