# Uma Formulação Robusta Indexada no Tempo para a Entrega de Concreto Usinado

Este repositório contém o código-fonte, as instâncias de teste e os scripts de análise para a dissertação de mestrado **"Uma Formulação Robusta Indexada no Tempo para a Entrega de Concreto Usinado: Roteamento com Múltiplas Plantas, Janelas de Tempo e Intervalos entre Entregas"**, defendida no Programa de Pós-Graduação em Engenharia de Produção da Universidade Federal de Minas Gerais (UFMG).

**Autor**: Lucas Araújo de Paula
**Orientador**: Prof. Dr. Ricardo Saraiva de Camargo

---

## 📜 Sobre o Projeto

Este trabalho aborda o **Problema de Entrega de Concreto (CDP)**, uma variação complexa e de grande relevância industrial do Problema de Roteamento de Veículos (VRP). A entrega de concreto usinado é uma operação logística crítica, com restrições rigorosas de tempo devido à natureza perecível do produto.

A principal contribuição desta pesquisa é o desenvolvimento e a validação de um **novo modelo de programação matemática de inteiros mistos (PLIM)**. Este modelo utiliza uma abordagem de **indexação temporal** que se mostrou computacionalmente mais eficiente e robusta do que formulações de referência da literatura, especialmente ao lidar com instâncias de maior escala e complexidade.

## 📂 Estrutura do Repositório

O projeto está organizado da seguinte forma para garantir a clareza e a reprodutibilidade dos experimentos:

```
.
├── Data/
│   └── kinable/
│       ├── setA/         # Conjunto de instâncias A de Kinable et al. (2014)
│       └── setB/         # Conjunto de instâncias B de Kinable et al. (2014)
├── model/
│   ├── authorial_1.py    # Implementação do modelo proposto (indexado no tempo)
│   ├── kinable_homo.py   # Implementação do modelo de Kinable et al. (adaptado para frota homogênea)
│   └── ..._lr.py         # Versões dos modelos para resolver a relaxação linear
├── Insts/                  # Instâncias processadas em formato .json (gerado pelo código)
├── results/                # Diretório onde os resultados (CSV) são salvos
├── images/                 # Gráficos e figuras gerados para a dissertação
├── main.py                 # Ponto de entrada principal para executar os experimentos
├── data.py                 # Módulo para leitura e processamento dos arquivos de instância
├── gen_*.py                # Scripts para gerar tabelas LaTeX e figuras de análise
└── README.md               # Este arquivo
```

## 🛠️ Modelos Implementados

Este repositório contém as implementações dos seguintes modelos, utilizando a API `docplex` do Python para o IBM CPLEX:

1.  **Modelo Proposto (`authorial_1.py`)**: A formulação inovadora baseada em indexação temporal, que discretiza o horizonte de planejamento e modela explicitamente a alocação de veículos de cada planta em cada instante de tempo.

2.  **Modelo de Kinable (`kinable_homo.py`)**: Nossa implementação do modelo de referência de Kinable et al. (2014), adaptado para uma frota homogênea a fim de garantir uma comparação justa. A formulação original é baseada em fluxo e sequenciamento de viagens.

A análise comparativa, detalhada na dissertação, demonstra que o Modelo Proposto obtém limites duais mais fortes, resultando em gaps de otimalidade menores e tempos de resolução significativamente mais rápidos para problemas complexos.

## 🚀 Como Executar

Para replicar os experimentos descritos na dissertação, siga os passos abaixo.

### Pré-requisitos

* **Python 3.8+**
* **IBM ILOG CPLEX Optimization Studio (v22.1 ou superior)**: O solver CPLEX deve estar instalado e sua biblioteca Python (`cplex`) acessível no ambiente.
* **Bibliotecas Python**: Instale as dependências necessárias.
    ```bash
    pip install pandas docplex matplotlib
    ```

### Execução dos Experimentos

1.  **Executar todos os experimentos**:
    Para rodar a bateria completa de testes em todas as instâncias dos conjuntos A e B, execute o script `main.py`. Ele irá iterar sobre os modelos e instâncias, aplicando o limite de tempo e salvando os resultados.
    ```bash
    python main.py
    ```
    **Atenção**: A execução completa é computacionalmente intensiva e pode levar vários dias, pois cada instância tem um limite de tempo de 3600 segundos.

2.  **Executar uma instância específica**:
    Para testar um modelo em uma única instância, edite o main e insira o número da instância desejada "insNumber".
    ```

### Análise dos Resultados

Após a execução, os resultados detalhados são salvos em um arquivo `.csv` no diretório `results/`. Para gerar os gráficos e tabelas apresentados na dissertação, utilize os scripts `gen_*.py`.

* `gen_table_results_ltx.py`: Gera a tabela comparativa principal em formato LaTeX.
* `gen_img_scatter_gap.py`: Gera o gráfico de dispersão dos gaps.
* `gen_img_scatter_LB.py`: Gera o gráfico de dispersão dos limites inferiores.
* `gen_img_scatter_time.py`: Gera o gráfico de dispersão dos tempos de execução.
* `gen_img_perfprof.py`: Gera o perfil de performance dos modelos.

## Citação

Se você utilizar este trabalho em sua pesquisa, por favor, cite a dissertação:

DE PAULA, L. A. and CAMARGO, R. S. **Uma Formulação Robusta Indexada no Tempo para a Entrega de Concreto Usinado: Roteamento com Múltiplas Plantas, Janelas de Tempo e Intervalos entre Entregas**. Dissertação (Mestrado em Engenharia de Produção) — Universidade Federal de Minas Gerais, Belo Horizonte, 2025.

```bibtex
@mastersthesis{Paula2025,
  author  = {de Paula, Lucas Araújo},
  advisor = {Camargo, Ricardo Saraiva de},
  title   = {Uma Formulação Robusta Indexada no Tempo para a Entrega de Concreto Usinado: Roteamento com Múltiplas Plantas, Janelas de Tempo e Intervalos entre Entregas},
  school  = {Universidade Federal de Minas Gerais},
  year    = {2025},
  address = {Belo Horizonte},
  type    = {Dissertação de Mestrado}
}
```

## Contato

Para dúvidas ou mais informações, sinta-se à vontade para entrar em contato.
