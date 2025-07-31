import data

author = 'kinable'
instances = data.listInsts(author, log=False)

# print("\\chapter{Resultados}")
# print("\\label{sec:results}")
print("\\begin{landscape}")
print("\\footnotesize")
print("\\begin{longtable}{lrrrrr rrrrr rrrr}")
print("\\caption{Resultados comparativos entre métodos}\\\\")
print("\\toprule")
print("\\label{tab:result}")

# Cabeçalhos
print("Instância & \\multicolumn{5}{c}{Novo modelo}& \\multicolumn{2}{c}{Relax. Lin.} & \\multicolumn{5}{c}{Kinable}& \\multicolumn{2}{c}{Relax. Lin.} \\\\")
print("\\cmidrule(lr){2-6}\\cmidrule(lr){7-8}  \\cmidrule(lr){9-13}\\cmidrule(lr){14-15}")
print(" & Obj & UB & \\textit{Gap} (\\%) & t(s) & Nb & Obj & t(s) & Obj & UB & \\textit{Gap} (\\%) & t(s) & Nb & Obj & t(s) \\\\")
print("\\midrule")
print("\\endfirsthead")

# Cabeçalhos para páginas seguintes
print("\\toprule")
print("Instância & \\multicolumn{5}{c}{Novo modelo}& \\multicolumn{2}{c}{Relax. Lin.} & \\multicolumn{5}{c}{Kinable}& \\multicolumn{2}{c}{Relax. Lin.} \\\\")
print("\\cmidrule(lr){2-6}\\cmidrule(lr){7-8}  \\cmidrule(lr){9-13}\\cmidrule(lr){14-15}")
print(" & Obj & UB & \\textit{Gap} (\\%) & t(s) & Nb & Obj & t(s) & Obj & UB & \\textit{Gap} (\\%) & t(s) & Nb & Obj & t(s) \\\\")
print("\\midrule")
print("\\endhead")

for multiplier in range(1, 11):
    for insNumber in range(1, instances + 1):
        i, j, k, seed = data.get_inst_parameters(insNumber, author)
        if j != 5 * multiplier:
            continue

        dt = data.get_data(insNumber, author)
        if None in (dt.md_authorial_1_cost, dt.md_authorial_1_best_integer,
                    dt.md_kinable_homo_cost, dt.md_kinable_homo_best_integer):
            continue

        a_cost = dt.md_authorial_1_cost
        a_lr_cost = dt.md_authorial_1_lr_cost
        a_ub = dt.md_authorial_1_best_integer
        a_time = dt.md_authorial_1_time
        a_lr_time = dt.md_authorial_1_lr_time
        a_nb = dt.md_authorial_1_nb_nodes

        k_cost = dt.md_kinable_homo_cost
        k_lr_cost = dt.md_kinable_homo_lr_cost
        k_ub = dt.md_kinable_homo_best_integer
        k_time = dt.md_kinable_homo_time
        k_lr_time = dt.md_kinable_homo_lr_time
        k_nb = dt.md_kinable_homo_nb_nodes

        a_Gap = (a_ub - a_cost) * 100 / a_ub if a_ub else 0
        k_Gap = (k_ub - k_cost) * 100 / k_ub if k_ub else 0

        linha = [
            f"{i}\\_{j}\\_{k}",
            int(round(a_cost)),
            round(a_ub, 2),
            round(a_Gap, 2),
            round(a_time, 2),
            int(a_nb),
            round(a_lr_cost, 2) if a_lr_cost else '-',
            round(a_lr_time, 2) if a_lr_cost else 3600,
            int(round(k_cost)),
            round(k_ub, 2),
            round(k_Gap, 2),
            round(k_time, 2),
            int(k_nb),
            round(k_lr_cost, 2),
            round(k_lr_time, 2),
        ]

        linha_formatada = " & ".join(str(v) if v is not None else "-" for v in linha)
        print(linha_formatada + " \\\\")

print("\\bottomrule")
print("\\end{longtable}")
print("\\end{landscape}")
