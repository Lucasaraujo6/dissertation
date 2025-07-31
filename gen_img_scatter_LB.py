import matplotlib.pyplot as plt
import numpy as np
import data
import matplotlib.lines as mlines # Import necessário para criar a legenda customizada

# --- Configurações Iniciais ---
author = 'kinable'
instances = data.listInsts(author, log=False)
dados_coletados = []

# --- 1. Loop para coletar todos os dados necessários ---
print("Coletando e processando dados das instâncias...")
for insNumber in range(1, instances + 1):
    i, j, k, seed = data.get_inst_parameters(insNumber, author)

    dt = data.get_data(insNumber, author)
    
    a_cost = dt.md_authorial_1_cost
    k_cost = dt.md_kinable_homo_cost

    # Pula a instância se algum dado de custo estiver faltando
    if a_cost is None or k_cost is None:
        continue
    
    # Adiciona TODOS os dados relevantes para cada instância
    dados_coletados.append({
        "i": i, # Quantidade de plantas
        "j": j, # Quantidade de clientes
        "a_cost": a_cost, # Limite Inferior do Proposto
        "k_cost": k_cost  # Limite Inferior do Kinable
    })

# Extrair listas de dados para plotagem
proposto_costs = [d['a_cost'] for d in dados_coletados]
kinable_costs = [d['k_cost'] for d in dados_coletados]
i_values = [d['i'] for d in dados_coletados]
j_values = [d['j'] for d in dados_coletados]

# --- 2. Preparação para o Gráfico com Múltiplos Atributos ---
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
for plant_type, marker_style in marker_map.items():
    x_subset, y_subset, color_subset = [], [], []
    for i in range(len(dados_coletados)):
        if i_values[i] == plant_type:
            # Usando os dados de CUSTO (Limite Inferior)
            x_subset.append(kinable_costs[i])
            y_subset.append(proposto_costs[i])
            color_subset.append(client_color_map[j_values[i]])
            
    ax.scatter(x_subset, y_subset, c=color_subset, marker=marker_style,
               label=f'{plant_type} plantas',
               s=70, alpha=0.8, edgecolors='k', linewidth=0.5)

# --- 4. Criação de Legendas Customizadas e Posicionadas ---

# 4a. Criar handles para a legenda de Plantas (SÍMBOLOS) com cor neutra
# (A criação dos handles não muda)
plant_legend_handles = [mlines.Line2D([], [], color='gray', marker=marker_map[plant],
                                     linestyle='None', markersize=10, 
                                     label=f'{plant} plantas') for plant in unique_plants]

# Posiciona a legenda de Plantas no canto inferior direito (será a da esquerda no par)
legend_plants = ax.legend(handles=plant_legend_handles, 
                          title='Nº de Plantas',
                          fontsize=12, title_fontsize=13,
                          loc='lower right', # <-- MUDANÇA: Ancora pelo canto inferior direito
                          bbox_to_anchor=(0.78, 0), # <-- MUDANÇA: Posição (x,y) ajustada
                          facecolor='white', framealpha=0.9)
# Adiciona a primeira legenda ao gráfico para que não seja sobrescrita
ax.add_artist(legend_plants)


# 4b. Criar handles para a legenda de Clientes (CORES)
# (A criação dos handles não muda)
color_legend_handles = [mlines.Line2D([], [], color=client_color_map[client], marker='o', 
                                     linestyle='None', markersize=10, 
                                     label=f'{client} clientes') for client in unique_clients]

# Posiciona a legenda de Clientes à direita da de Plantas
ax.legend(handles=color_legend_handles, 
          title='Nº de Clientes',
          fontsize=14, title_fontsize=15,
          loc='lower right', # <-- MUDANÇA: Ancora pelo mesmo canto
          bbox_to_anchor=(0.99, 0), # <-- MUDANÇA: Posição X mais à direita
          facecolor='white', framealpha=0.9)
# --- 5. Ajustes Finais do Gráfico ---

# Linha de referência y=x
min_val = min(min(kinable_costs), min(proposto_costs))
max_val = max(max(kinable_costs), max(proposto_costs))
ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='_nolegend_')

# Rótulos, Título e Grid
ax.set_xlabel('Limite Inferior - Kinable', fontsize=16)
ax.set_ylabel('Limite Inferior - Proposto', fontsize=16)
ax.grid(True, linestyle='--')

# Ajusta os limites dos eixos com uma pequena margem
ax.set_xlim(left=min_val*0.98, right=max_val*1.02)
ax.set_ylim(bottom=min_val*0.98, top=max_val*1.02)
ax.tick_params(axis='x', labelsize=14)
ax.tick_params(axis='y', labelsize=14)

plt.tight_layout()
nome_arquivo_scatter_custos = "img_scatter_LB.png"
plt.savefig(nome_arquivo_scatter_custos, dpi=300)
print(f"Gráfico de dispersão de limites inferiores salvo como: {nome_arquivo_scatter_custos}")