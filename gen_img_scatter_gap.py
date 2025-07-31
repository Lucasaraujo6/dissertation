import matplotlib.pyplot as plt
import numpy as np
import data
import matplotlib.lines as mlines # Import necessário para criar a legenda customizada

# --- Configurações Iniciais ---
author = 'kinable'
instances = data.listInsts(author, log=False)
dados_coletados = []

# --- 1. Loop para coletar todos os dados necessários (i, j, k, gaps) ---
print("Coletando e processando dados das instâncias...")
for insNumber in range(1, instances + 1):
    i, j, k, seed = data.get_inst_parameters(insNumber, author)

    dt = data.get_data(insNumber, author)
    
    a_cost = dt.md_authorial_1_cost
    a_ub = dt.md_authorial_1_best_integer
    k_cost = dt.md_kinable_homo_cost
    k_ub = dt.md_kinable_homo_best_integer

    if None in (a_cost, a_ub, k_cost, k_ub) or a_ub == 0 or k_ub == 0:
        continue
    
    dados_coletados.append({
        "i": i, # Quantidade de plantas
        "j": j, # Quantidade de clientes
        "gap_auth": (a_ub - a_cost) * 100 / a_ub if a_ub > 0 else 0,
        "gap_kin": (k_ub - k_cost) * 100 / k_ub if k_ub > 0 else 0
    })

# Extrair listas de dados para plotagem
gaps_auth = [d['gap_auth'] for d in dados_coletados]
gaps_kin = [d['gap_kin'] for d in dados_coletados]
i_values = [d['i'] for d in dados_coletados]
j_values = [d['j'] for d in dados_coletados]

# --- 2. Preparação dos Mapeamentos de Cor e Símbolo ---
fig, ax = plt.subplots(figsize=(12, 10))

# Mapeamento para SÍMBOLOS: Quantidade de Plantas (i) -> Símbolo (marker)
unique_plants = sorted(list(set(i_values)))
markers = ['o', '^', 's', 'D', 'v', 'P', '*', 'X']
marker_map = {plant: markers[i % len(markers)] for i, plant in enumerate(unique_plants)}

# Mapeamento para CORES: Quantidade de Clientes (j) -> Cor
unique_clients = sorted(list(set(j_values)))
color_palette = plt.get_cmap('tab10')
client_color_map = {client: color_palette(i) for i, client in enumerate(unique_clients)}

# --- 3. Plotagem Iterativa ---
# (Esta seção permanece igual)
for plant_type, marker_style in marker_map.items():
    x_subset, y_subset, color_subset = [], [], []
    for i in range(len(dados_coletados)):
        if i_values[i] == plant_type:
            x_subset.append(gaps_kin[i])
            y_subset.append(gaps_auth[i])
            color_subset.append(client_color_map[j_values[i]])
            
    ax.scatter(x_subset, y_subset, c=color_subset, marker=marker_style,
               s=60, alpha=0.8, edgecolors='k', linewidth=0.5)

# --- 4. Criação de Legendas Customizadas e Posicionadas ---

# 4a. Criar handles para a legenda de Clientes (CORES)
color_legend_handles = [mlines.Line2D([], [], color=client_color_map[client], marker='o', 
                                     linestyle='None', markersize=10, 
                                     label=f'{client} clientes') for client in unique_clients]

# Posiciona a legenda de Clientes no canto superior esquerdo
legend_clients = ax.legend(handles=color_legend_handles, 
                           title='Nº de Clientes',
                           fontsize=14, title_fontsize=15,
                           loc='upper left', # Ancora a legenda pelo seu canto superior esquerdo
                           bbox_to_anchor=(0.01, 0.99), # Posição (x,y) no gráfico (0,0 a 1,1)
                           facecolor='white', framealpha=0.9) # Fundo branco e semi-transparente
# Adiciona a primeira legenda ao gráfico para que não seja sobrescrita
ax.add_artist(legend_clients)


# 4b. Criar handles para a legenda de Plantas (SÍMBOLOS) com cor neutra
plant_legend_handles = [mlines.Line2D([], [], color='gray', marker=marker_map[plant], # Cor cinza neutra
                                     linestyle='None', markersize=10, 
                                     label=f'{plant} plantas') for plant in unique_plants]

# Posiciona a legenda de Plantas à direita da primeira
ax.legend(handles=plant_legend_handles, 
          title='Nº de Plantas',
          fontsize=12, title_fontsize=13,
          loc='upper left', # Ancora pelo canto superior esquerdo
          bbox_to_anchor=(0.25, 0.99), # Posição X deslocada para a direita
          facecolor='white', framealpha=0.9) # Fundo branco

# --- 5. Ajustes Finais do Gráfico ---

# Linha de referência y=x
ax.plot([0, 100], [0, 100], 'r--', label='_nolegend_')

# Rótulos, Título e Grid
ax.set_xlabel('Gap do Modelo de Kinable (%)', fontsize=16)
ax.set_ylabel('Gap do Modelo Proposto (%)', fontsize=16)
ax.grid(True, linestyle='--')
ax.set_xlim(left=-2, right=102)
ax.tick_params(axis='x', labelsize=14)
ax.tick_params(axis='y', labelsize=14)
ax.set_ylim(bottom=-2, top=102)

plt.tight_layout()
nome_arquivo_scatter_multi = "img_scatter_gap.png"
plt.savefig(nome_arquivo_scatter_multi, dpi=300)
print(f"Gráfico de dispersão com múltiplas legendas posicionadas salvo como: {nome_arquivo_scatter_multi}")