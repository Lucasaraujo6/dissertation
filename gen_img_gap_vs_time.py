import matplotlib.pyplot as plt
import data

# Inicialização
nomes_instancias = []
tempo_dif_norm = []
gap_dif_norm = []

author = 'kinable'
instances = data.listInsts(author, log=False)
setA = 0

# Loop principal de coleta de dados
for multiplier in range(11):
    for insNumber in range(1, instances + 1):
        i, j, k, seed = data.get_inst_parameters(insNumber, author)
        if j != 5 * multiplier:
            continue
        if setA and k >= 6:
            continue
        if not setA and k < 6:
            continue

        nome = f"{i}_{j}_{k}"
        dt = data.get_data(insNumber, author)
        if None in (dt.md_authorial_1_time,dt.md_kinable_homo_time): continue
        t_auth = dt.md_authorial_1_time/60
        t_kin = dt.md_kinable_homo_time/60

        a_cost = dt.md_authorial_1_cost
        a_ub = dt.md_authorial_1_best_integer
        k_cost = dt.md_kinable_homo_cost
        k_ub = dt.md_kinable_homo_best_integer

        if None in (t_auth, t_kin, a_cost, a_ub, k_cost, k_ub):
            continue
        if a_ub == 0 or k_ub == 0:  # evita divisão por zero
            continue

        # Gap calculado manualmente
        g_auth = (a_ub - a_cost) *100 / a_ub
        g_kin = (k_ub - k_cost) *100/ k_ub

        # Adiciona os dados às listas
        nomes_instancias.append(nome)
        tempo_dif_norm.append((t_auth, t_kin))
        gap_dif_norm.append((g_auth, g_kin))

# ========================
# Parte do gráfico começa aqui
# ========================

# Construção de estrutura para ordenação (pela diferença absoluta entre gaps)
labels_para_plot = []
for nome, (t_auth, t_kin), (g_auth, g_kin) in zip(nomes_instancias, tempo_dif_norm, gap_dif_norm):
    gap_diff = ( g_kin-g_auth)
    labels_para_plot.append((nome, int(t_auth), t_kin, g_auth, g_kin, gap_diff))

# Ordenar pela diferença absoluta entre gaps
labels_para_plot.sort(key=lambda x: x[1])  # x[5] = abs_diff
labels_para_plot.sort(key=lambda x: x[5])  # x[5] = abs_diff

# Reorganizar as listas já ordenadas
nomes_ordenados   = [x[0] for x in labels_para_plot]
t_auth_ordenado   = [x[1] for x in labels_para_plot]
t_kin_ordenado    = [x[2] for x in labels_para_plot]
g_auth_ordenado   = [-x[3] for x in labels_para_plot]  # negativo para ir para baixo
g_kin_ordenado    = [-x[4] for x in labels_para_plot]  # negativo para ir para baixo

# Posição das barras
x = range(len(nomes_ordenados))
bar_width = 0.35

fig, ax = plt.subplots(figsize=(14, 6))

# Barras de tempo (acima do eixo)
ax.bar([i - bar_width/2 for i in x], t_kin_ordenado, width=bar_width, label='Tempo - Kinable', color='skyblue')
ax.bar([i + bar_width/2 for i in x], t_auth_ordenado, width=bar_width, label='Tempo - Proposto', color='navy')

# Barras de gap (abaixo do eixo)
ax.bar([i - bar_width/2 for i in x], g_kin_ordenado, width=bar_width, label='Gap - Kinable', color='salmon')
ax.bar([i + bar_width/2 for i in x], g_auth_ordenado, width=bar_width, label='Gap - Proposto', color='darkred')

# Linha central
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')

# Rótulos e ajustes
ax.set_xticks(x)
ax.set_xticklabels(nomes_ordenados, rotation=90, fontsize=10)
ax.set_ylabel(' Gap (%) / Tempo (min)', fontsize=16)
ax.set_xlabel('Instância', fontsize=16)
# ax.set_title('Comparação entre Tempo e Gap: Auth vs Kin')
ax.tick_params(axis='y', labelsize=14)
ax.legend(
    fontsize=12,
    loc='upper left',  # "Ancora" a legenda pelo seu canto superior esquerdo
    bbox_to_anchor=(0.11, 0.25)  # Posiciona essa âncora no ponto (x=1.01, y=1)
                                # (um pouco para fora do lado direito e alinhado ao topo)
)
ax.set_xlim(-1, len(nomes_ordenados) )

ax.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
# Salvar imagem
if setA:
    plt.savefig("img_setA_barra_normalizada_tempo_gap.png", dpi=300, bbox_inches='tight')
else:
    plt.savefig("img_setB_barra_normalizada_tempo_gap.png", dpi=300, bbox_inches='tight')
# plt.savefig("img_gap_vs_time.png", dpi=300, bbox_inches='tight')

