import matplotlib.pyplot as plt
import data

# --- Lógica de Set A / Set B ---
# Defina setA = 1 para Set A (k < 6) ou setA = 0 para Set B (k >= 6)
# setA = 0
# --------------------------------

author = 'kinable'
instances = data.listInsts(author, log=False)

# Lista para armazenar dados de forma estruturada
dados_coletados = []

# Etapa 1: Loop único para coletar, filtrar e processar os dados
for insNumber in range(1, instances + 1):
    i, j, k, seed = data.get_inst_parameters(insNumber, author)

    # Lógica de filtro aplicada no início
    # if setA and k >= 6:
    #     continue
    # if not setA and k < 6:
    #     continue

    # Pega os dados apenas para as instâncias que passaram no filtro
    dt = data.get_data(insNumber, author)
    
    a_cost = dt.md_authorial_1_cost
    a_ub = dt.md_authorial_1_best_integer
    k_cost = dt.md_kinable_homo_cost
    k_ub = dt.md_kinable_homo_best_integer

    # Pula a instância se algum dado estiver faltando
    if None in (a_cost, a_ub, k_cost, k_ub) or a_ub == 0 or k_ub == 0:
        continue
        
    # Cálculos
    g_auth = (a_ub - a_cost) * 100 / a_ub
    g_kin = (k_ub - k_cost) * 100 / k_ub
    g_diff = g_kin - g_auth
    nome = f"{i}_{j}_{k}"
     
    # Armazena todos os dados relevantes juntos
    dados_coletados.append({
        "nome": nome,
        "a_cost": a_cost,
        "a_ub": a_ub,
        "k_cost": k_cost,
        "k_ub": k_ub,
        "g_diff": g_diff
    })

# Etapa 2: Ordenar a lista de dados coletados pela diferença de Gap
# O gráfico final será ordenado do método que mais favorece o 'Proposto' para o que mais favorece 'Kinable'
dados_coletados.sort(key=lambda item: item['g_diff'])

# Etapa 3: "Descompactar" os dados em listas separadas para a plotagem
# Isso garante que todas as listas estejam na mesma ordem
nomes_instancias = [d['nome'] for d in dados_coletados]
authorial_1_costs = [d['a_cost'] for d in dados_coletados]
authorial_1_upper_bounds = [d['a_ub'] for d in dados_coletados]
kinable_homo_costs = [d['k_cost'] for d in dados_coletados]
kinable_homo_upper_bounds = [d['k_ub'] for d in dados_coletados]
g_diffs = [d['g_diff'] for d in dados_coletados]
# Adicione este bloco após a Etapa 3 do seu código original

# --- Estratégia 1: Gráfico de Dispersão (Scatter Plot) ---

gaps_auth = [(d['a_ub'] - d['a_cost']) * 100 / d['a_ub'] if d['a_ub'] > 0 else 0 for d in dados_coletados]
gaps_kin = [(d['k_ub'] - d['k_cost']) * 100 / d['k_ub'] if d['k_ub'] > 0 else 0 for d in dados_coletados]

fig_scatter, ax_scatter = plt.subplots(figsize=(8, 8))

ax_scatter.scatter(gaps_kin, gaps_auth, alpha=0.7, edgecolors='k')

# Linha de referência y=x
max_gap = max(max(gaps_kin), max(gaps_auth))
ax_scatter.plot([0, max_gap], [0, max_gap], 'r--', label='Desempenho Igual')

# Rótulos e Título
ax_scatter.set_xlabel('Gap do Modelo de Kinable (%)', fontsize=14)
ax_scatter.set_ylabel('Gap do Modelo Proposto (%)', fontsize=14)
# ax_scatter.set_title('Comparação Direta de Gaps por Instância', fontsize=16)
ax_scatter.grid(True, linestyle='--')
ax_scatter.legend()
ax_scatter.set_xlim(left=-1) # Garante que o 0 seja visível
ax_scatter.set_ylim(bottom=-1)

plt.tight_layout()
# nome_arquivo_scatter = f"img_scatter_gap_{'setA' if setA else 'setB'}.png"
nome_arquivo_scatter = f"img_scatter_gap.png"
plt.savefig(nome_arquivo_scatter, dpi=300)
print(f"Gráfico de dispersão salvo como: {nome_arquivo_scatter}")

# # --- Início do gráfico ---
# fig, ax = plt.subplots(figsize=(14, 7))
# x = range(len(nomes_instancias))

# # Plot das curvas
# ax.plot(x, kinable_homo_upper_bounds, marker='v', linestyle='--', label='Limite Superior - Kinable', color='lightgreen')
# ax.plot(x, authorial_1_upper_bounds, marker='^', linestyle='--', label='Limite Superior - Proposto', color='lightblue')
# ax.plot(x, kinable_homo_costs, marker='s', markersize=10, linestyle='-', label='Função Objetivo - Kinable', color='green')
# ax.plot(x, authorial_1_costs, marker='o', markersize=5, linestyle='-', label='Função Objetivo - Proposto', color='blue')

# # Eixos e Título
# ax.set_xticks(x)
# ax.set_xticklabels(nomes_instancias, rotation=90, fontsize=8) # Fonte menor para caber mais instâncias
# ax.set_ylabel('Volume', fontsize=16)
# ax.set_xlabel('Instância', fontsize=16)
# # ax.set_title(f"Comparativo de Limites e Volumes - {'Set A' if setA else 'Set B'}", fontsize=18)

# # Ticks dos eixos
# ax.tick_params(axis='y', labelsize=14)

# # Grid e legenda
# ax.grid(True, linestyle='--', alpha=0.5)

# ax.legend(
#     fontsize=12,
#     loc='upper left',  # "Ancora" a legenda pelo seu canto superior esquerdo
#     bbox_to_anchor=(0.12, 1)  # Posiciona essa âncora no ponto (x=1.01, y=1)
#                               # (um pouco para fora do lado direito e alinhado ao topo)
# )


# ax.set_xlim(-1, len(authorial_1_costs) )
# plt.tight_layout()

# # Salvar imagem com nome dinâmico
# nome_arquivo = f"img_lb_vs_ub_{'setA' if setA else 'setB'}.png"
# plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')

# print(f"Gráfico salvo como: {nome_arquivo}")