import matplotlib.pyplot as plt
import numpy as np
import data
import matplotlib.lines as mlines # Import necessário para criar a legenda customizada

# --- Configurações Iniciais ---
author = 'kinable'
instances = data.listInsts(author, log=False)
dados_coletados = []
# Usaremos o tempo limite real para marcar o gráfico
TIME_LIMIT = 3600.0 

# --- 1. Loop para coletar todos os dados necessários ---
print("Coletando e processando dados das instâncias...")
for insNumber in range(1, instances + 1):
    i, j, k, seed = data.get_inst_parameters(insNumber, author)

    dt = data.get_data(insNumber, author)
    
    auth_time_raw = dt.md_authorial_1_time
    kin_time_raw = dt.md_kinable_homo_time

    if auth_time_raw is None or kin_time_raw is None:
        continue
    
    # Adiciona TODOS os dados relevantes para cada instância
    dados_coletados.append({
        "i": i, # Quantidade de plantas
        "j": j, # Quantidade de clientes
        "auth_time": auth_time_raw,
        "kin_time": kin_time_raw
    })

# Extrair listas de dados para plotagem
proposto_times = [d['auth_time'] for d in dados_coletados]
kinable_times = [d['kin_time'] for d in dados_coletados]
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
# Adicionamos um valor pequeno para evitar problemas com log(0)
for plant_type, marker_style in marker_map.items():
    x_subset, y_subset, color_subset = [], [], []
    for i in range(len(dados_coletados)):
        if i_values[i] == plant_type:
            x_subset.append(kinable_times[i] + 0.01) # Adiciona pequeno valor
            y_subset.append(proposto_times[i] + 0.01) # Adiciona pequeno valor
            color_subset.append(client_color_map[j_values[i]])
            
    ax.scatter(x_subset, y_subset, c=color_subset, marker=marker_style,
               label=f'{plant_type} plantas',
               s=70, alpha=0.8, edgecolors='k', linewidth=0.5)

# --- 4. Criação de Legendas Customizadas e Posicionadas ---
# (Lógica e posicionamento idênticos ao seu script de Limites Inferiores)

# 4a. Legenda de Plantas (SÍMBOLOS)
plant_legend_handles = [mlines.Line2D([], [], color='gray', marker=marker_map[plant],
                                     linestyle='None', markersize=10, 
                                     label=f'{plant} plantas') for plant in unique_plants]

legend_plants = ax.legend(handles=plant_legend_handles, 
                          title='Nº de Plantas',
                          fontsize=12, title_fontsize=13,
                          loc='lower right',
                          bbox_to_anchor=(0.78, 0.01), # Posição no canto inferior
                          facecolor='white', framealpha=0.9)
ax.add_artist(legend_plants)

# 4b. Legenda de Clientes (CORES)
color_legend_handles = [mlines.Line2D([], [], color=client_color_map[client], marker='o', 
                                     linestyle='None', markersize=10, 
                                     label=f'{client} clientes') for client in unique_clients]

ax.legend(handles=color_legend_handles, 
          title='Nº de Clientes',
          fontsize=12, title_fontsize=13, # Fontes ligeiramente ajustadas para consistência
          loc='lower right',
          bbox_to_anchor=(0.99, 0.01), # Posição no canto inferior
          facecolor='white', framealpha=0.9)

# --- 5. Ajustes Finais do Gráfico ---

# APLICANDO A ESCALA LOGARÍTMICA
ax.set_xscale('log')
ax.set_yscale('log')

# Linha de referência y=x
min_val = 0.01 # Mínimo para o plot log
max_val = max(max(proposto_times), max(kinable_times)) * 1.5
ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='_nolegend_')

# Linhas de tempo limite para indicar falhas
ax.axhline(TIME_LIMIT, color='gray', linestyle=':', lw=2)
ax.axvline(TIME_LIMIT, color='gray', linestyle=':', lw=2)

# Rótulos, Título e Grid
ax.set_xlabel('Tempo de Execução - Kinable (s) [Escala Log]', fontsize=16)
ax.set_ylabel('Tempo de Execução - Proposto (s) [Escala Log]', fontsize=16)
# ax.set_title('Comparação de Tempos de Execução (Cor por Clientes, Símbolo por Plantas)', fontsize=18)
ax.grid(True, which="both", linestyle='--') # 'which="both"' para grades em escala log

# Ajusta os limites dos eixos
ax.set_xlim(left=min_val*0.9)
ax.set_ylim(bottom=min_val*0.9)
ax.tick_params(axis='x', labelsize=14)
ax.tick_params(axis='y', labelsize=14)

plt.tight_layout()
nome_arquivo_scatter_tempos = "img_scatter_time.png"
plt.savefig(nome_arquivo_scatter_tempos, dpi=300)
print(f"Gráfico de dispersão de tempos salvo como: {nome_arquivo_scatter_tempos}")