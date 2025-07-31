import matplotlib.pyplot as plt
import numpy as np
import data # Certifique-se que seu módulo 'data.py' está sendo importado

# --- 1. COLETA E ESTRUTURAÇÃO DOS DADOS ---

# Lista para armazenar os dados de forma estruturada
all_data = []

author = 'kinable'
instances = data.listInsts(author, log=False) # USANDO SEU MÉTODO REAL
# setA = 0 

# Loop principal de coleta de dados
for insNumber in range(1, instances + 1):
    # USANDO SEUS MÉTODOS REAIS PARA OBTER OS DADOS
    i, j, k, seed = data.get_inst_parameters(insNumber, author)
    dt = data.get_data(insNumber, author)

    # Filtros do seu código original
#     if setA and k >= 6:
#         continue
#     if not setA and k < 6:
#         continue

    # Extração e verificação dos dados
    if None in (dt.md_authorial_1_time, dt.md_kinable_homo_time): continue
    t_auth = dt.md_authorial_1_time / 60
    t_kin = dt.md_kinable_homo_time / 60

    a_cost = dt.md_authorial_1_cost
    a_ub = dt.md_authorial_1_best_integer
    k_cost = dt.md_kinable_homo_cost
    k_ub = dt.md_kinable_homo_best_integer

    if None in (t_auth, t_kin, a_cost, a_ub, k_cost, k_ub) or a_ub == 0 or k_ub == 0:
        continue

    g_auth = (a_ub - a_cost) * 100 / a_ub
    g_kin = (k_ub - k_cost) * 100 / k_ub

    # Adiciona um dicionário à lista, associando os resultados ao seu grupo 'j'
    all_data.append({
        'j': j,
        't_auth': t_auth,
        't_kin': t_kin,
        'g_auth': g_auth,
        'g_kin': g_kin
    })

# --- 2. AGRUPAMENTO DOS DADOS POR 'j' ---

grouped_data = {}
for item in all_data:
    j_group = item['j']
    if j_group not in grouped_data:
        grouped_data[j_group] = {'t_auth': [], 't_kin': [], 'g_auth': [], 'g_kin': []}
    
    grouped_data[j_group]['t_auth'].append(item['t_auth'])
    grouped_data[j_group]['t_kin'].append(item['t_kin'])
    grouped_data[j_group]['g_auth'].append(item['g_auth'])
    grouped_data[j_group]['g_kin'].append(item['g_kin'])

sorted_groups = sorted(grouped_data.keys())
data_t_auth = [grouped_data[g]['t_auth'] for g in sorted_groups]
data_t_kin = [grouped_data[g]['t_kin'] for g in sorted_groups]
data_g_auth = [grouped_data[g]['g_auth'] for g in sorted_groups]
data_g_kin = [grouped_data[g]['g_kin'] for g in sorted_groups]

# --- 3. GERAÇÃO DOS GRÁFICOS DE BOXPLOT (ESTA PARTE ESTAVA CORRETA) ---

x_positions = np.arange(len(sorted_groups))
width = 0.35
color_auth = 'navy'
color_kin = 'skyblue'

# GRÁFICO DE TEMPO (Sem alterações)
fig1, ax1 = plt.subplots(figsize=(14, 7))
bp_auth = ax1.boxplot(data_t_auth, positions=x_positions - width/2, widths=width, patch_artist=True, boxprops=dict(facecolor=color_auth), medianprops=dict(color='white', linewidth=2))
bp_kin = ax1.boxplot(data_t_kin, positions=x_positions + width/2, widths=width, patch_artist=True, boxprops=dict(facecolor=color_kin), medianprops=dict(color='black', linewidth=2))
ax1.set_ylabel('Tempo de Execução (min)', fontsize=16)
ax1.set_xlabel('Grupos de Instâncias (j)', fontsize=16)
ax1.set_title('Comparação do Tempo de Execução por Grupo', fontsize=18)
ax1.set_xticks(x_positions)
ax1.set_xticklabels(sorted_groups, fontsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend([bp_auth["boxes"][0], bp_kin["boxes"][0]], ['Proposto', 'Kinable'], loc='upper left', fontsize=14)
plt.tight_layout()
plt.savefig("img_boxplot_tempo_corrigido.png", dpi=300)
plt.show()

# GRÁFICO DE GAP (Sem alterações)
fig2, ax2 = plt.subplots(figsize=(14, 7))
bp_auth_g = ax2.boxplot(data_g_auth, positions=x_positions - width/2, widths=width, patch_artist=True, boxprops=dict(facecolor=color_auth), medianprops=dict(color='white', linewidth=2))
bp_kin_g = ax2.boxplot(data_g_kin, positions=x_positions + width/2, widths=width, patch_artist=True, boxprops=dict(facecolor=color_kin), medianprops=dict(color='black', linewidth=2))
ax2.set_ylabel('Gap de Otimização (%)', fontsize=16)
ax2.set_xlabel('Grupos de Instâncias (j)', fontsize=16)
ax2.set_title('Comparação do Gap de Otimização por Grupo', fontsize=18)
ax2.set_xticks(x_positions)
ax2.set_xticklabels(sorted_groups, fontsize=12)
ax2.tick_params(axis='y', labelsize=12)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend([bp_auth_g["boxes"][0], bp_kin_g["boxes"][0]], ['Proposto', 'Kinable'], loc='upper right', fontsize=14)
plt.tight_layout()
plt.savefig("img_boxplot_gap_corrigido.png", dpi=300)
plt.show()