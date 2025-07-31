import numpy as np
import matplotlib.pyplot as plt
import data

# --- Configurações Iniciais ---
author = 'kinable'
instances = data.listInsts(author, log=False)
times = []
# Adicionamos uma lista para guardar os nomes das instâncias para a depuração
instance_details = [] 
names = ['Proposto', 'Kinable']
PENALTY_TIME = 7200.0

# --- 1. Coleta e Pré-processamento dos Dados ---
print("Coletando e processando dados das instâncias...")
# ESTRUTURA DE LOOP CORRIGIDA E EFICIENTE
for insNumber in range(1, instances + 1):
    i, j, k, seed = data.get_inst_parameters(insNumber, author)
    
    # Vamos focar apenas nos grupos de instâncias que você estava usando
    if j not in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:
        continue
          
    dt = data.get_data(insNumber, author)

    if dt.md_authorial_1_time is None or dt.md_kinable_homo_time is None:
        continue
    
    auth_time = dt.md_authorial_1_time if dt.md_authorial_1_time < 3600 else PENALTY_TIME
    kin_time = dt.md_kinable_homo_time if dt.md_kinable_homo_time < 3600 else PENALTY_TIME
    
    times.append([auth_time, kin_time])
    instance_details.append(f"Ins_{i}_{j}_{k}")

times = np.array(times)
     
# --- 2. Cálculo dos Ratios de Performance ---
ratios = times / np.min(times, axis=1)[:, np.newaxis]
ratios = np.maximum(ratios, 1.0)

# --- 3. Bloco de Investigação Forense (Impresso no Terminal) ---
# ==============================================================================
# INVESTIGAÇÃO FORENSE DAS VITÓRIAS
# ==============================================================================
total_instancias = ratios.shape[0]
vitorias_matrix = (ratios == 1.0) & (times < PENALTY_TIME)

proposto_vitorias_indices = np.where(vitorias_matrix[:, 0])[0]
kinable_vitorias_indices = np.where(vitorias_matrix[:, 1])[0]

print("\n" + "="*60)
print("INVESTIGAÇÃO FORENSE DAS VITÓRIAS REAIS (TEMPO < 1H)")
print("="*60)
print(f"Total de instâncias analisadas: {total_instancias}")

print(f"\n--- Análise de Vitórias para 'Proposto' ({len(proposto_vitorias_indices)} vitórias) ---")
for idx in proposto_vitorias_indices:
    print(f"Instância: {instance_details[idx]:<15} | Tempos: [Proposto={times[idx, 0]:.2f}, Kinable={times[idx, 1]:.2f}]")

print(f"\n--- Análise de Vitórias para 'Kinable' ({len(kinable_vitorias_indices)} vitórias) ---")
for idx in kinable_vitorias_indices:
    print(f"Instância: {instance_details[idx]:<15} | Tempos: [Proposto={times[idx, 0]:.2f}, Kinable={times[idx, 1]:.2f}]")

# Verificação final do empate
if np.array_equal(proposto_vitorias_indices, kinable_vitorias_indices):
    print("\n[!!!] CONCLUSÃO DA INVESTIGAÇÃO: Os índices de vitória são IDÊNTICOS.")
    print("      Isso confirma que, para os dados que o script está lendo, sempre que um método vence, o outro também vence com o mesmo tempo.")
    print("      O 'bug' não está neste script de análise, mas sim na fonte dos dados (data.py ou os arquivos de resultados que ele lê).")
else:
    print("\n[OK] CONCLUSÃO DA INVESTIGAÇÃO: Os índices de vitória são DIFERENTES, como esperado.")

print("="*60 + "\n")
# ==============================================================================
# FIM DA INVESTIGAÇÃO
# ==============================================================================


# --- 4. Geração do Gráfico de Perfil de Performance ---
print("Gerando o gráfico de perfil de performance...")
taus = np.linspace(1, np.max(ratios), 500)
profiles = [(ratios <= tau).mean(axis=0) for tau in taus]
profiles = np.array(profiles)

plt.figure(figsize=(10, 6))
for i, name in enumerate(names):
     plt.plot(taus, profiles[:, i], label=name, lw=2)

plt.xlabel(r'$\tau$ (Fator sobre o melhor tempo por instância)', fontsize=14)
plt.ylabel('Fração de instâncias', fontsize=14)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("img_perf_prof.png",  bbox_inches='tight')
print("Gráfico 'img_perf_prof.png' gerado com sucesso.")