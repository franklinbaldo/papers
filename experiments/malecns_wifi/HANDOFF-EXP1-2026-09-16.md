---
type: "Handoff Note"
title: "Handoff Operacional — MultiEURLEX Exp. 1 & Algorithmic Morphogenesis"
description: "Transição de contexto operacional e metodológico para continuação da execução do Experimento 1 em outra máquina."
tags: [malecns, handoff, multieurlex, exp1, algorithmic-connectome]
timestamp: 2026-09-16T12:16:30-04:00
---

# Handoff Operacional — 2026-09-16 (Sessão 2)

> **Nota de Transição de Contexto:** Documento preparado para retomada imediata do trabalho em outra máquina ou sessão.

---

## 1. Estado Atual do Repositório Git
- **Repositório:** `C:\Users\76450694220\workspace\papers`
- **Branch:** `feature/algorithmic-connectome-paper`
- **PR no GitHub:** https://github.com/franklinbaldo/papers/pull/470
- **Último Commit Sincronizado na Remota:** [`2c431a2`](https://github.com/franklinbaldo/papers/commit/2c431a2) (`feat(exp1): add frozen MultiEURLEX-21 runner with 10-fold nested CV`).
- **Estado de Trabalho Local:** Clean (`git status` limpo; scripts e papers sincronizados).

---

## 2. O que Foi Concluído Nesta Sessão

### A. Formalização Teórica nos Papers
1. **Model 4: Spectral Graph Fourier Morphogenetic Synthesis:**
   - Formalizado no [Paper 1 (`PAPER-ALGORITHMIC-CONNECTOME-2026.md`)](file:///C:/Users/76450694220/workspace/papers/experiments/malecns_wifi/PAPER-ALGORITHMIC-CONNECTOME-2026.md#L160).
   - Decomposição Laplaciana espectral $\mathbf{L} = \mathbf{U} \mathbf{\Lambda} \mathbf{U}^\top$ com parametrização contínua e analítica via inverse GFT.
   - Diferenciabilidade analítica estrita com respeito aos coeficientes harmônicos: $\frac{\partial \mathbf{W}^*}{\partial c_k} = \mathbf{u}_k \mathbf{u}_k^\top$.
2. **Os 1.314 Neurônios Descendentes como "Harmonic Knobs":**
   - Integrado na [Seção 7.3 do Paper 1](file:///C:/Users/76450694220/workspace/papers/experiments/malecns_wifi/PAPER-ALGORITHMIC-CONNECTOME-2026.md#L330).
   - Resolução do gargalo dimensional de $10^7$ conexões: a camada motora descendente de 1.314 canais atua como botões contínuos que controlam frequências espaciais (macro-simetria $\to$ tráfego de neurópilos $\to$ textura métrica de Peters).
3. **Programa da Mosca Pós-Evolutiva (Otimização Bi-Objetivo):**
   - Formalização dos dois eixos de Pareto:
     $$\max_{\boldsymbol{\theta}} \quad \Big( \mathcal{F}_{\text{behavioral}}\big(\mathcal{G}(\boldsymbol{\theta})\big), \;\; \mathcal{I}_{\text{biological}}\big(\mathcal{G}(\boldsymbol{\theta}), \mathcal{G}_{\text{bio}}\big) \Big)$$
   - Superação da falsa dicotomia "biológico vs. nulo cego", buscando a região topológica onde o conectoma procedural supera a biologia em robustez, fiação e sobrevivência mantendo a sintaxe de atratores biológicos.

### B. Implementação do Experimento 1 (Massive-Scale MultiEURLEX-21)
- **Script:** [`scripts/run_multieurlex_exp1.py`](file:///C:/Users/76450694220/workspace/papers/experiments/malecns_wifi/scripts/run_multieurlex_exp1.py).
- **Bundle de Dados Congelado:** `artifacts/runtime-v1/multieurlex-1000-features.npz` (1.000 chunks determinísticos do conjunto de teste português, 477 documentos completos, 21 classes EuroVoc, embeddings MiniLM 384d).
- **Protocolo de Avaliação Congelado:**
  - Validação cruzada aninhada de 10 dobras por documento (`nested 10-fold CV`).
  - Grade de 7 ganhos: $\rho \in \{0.0, 0.25, 0.5, 0.95, 1.5, 2.5, 4.0\}$.
  - Seleção interna de penalidade ridge: $\lambda \in \{0.01, 0.1, 1.0, 10.0, 100.0\}$.
  - 3 sementes confirmatórias pareadas: `0, 1, 2`.

---

## 3. Estado da Execução do Experimento 1

### Baselines Diretas Concluídas (12/12 células prontas):
| Condição | Seed 0 | Seed 1 | Seed 2 | Média $\pm$ Desvio |
| :--- | :---: | :---: | :---: | :---: |
| **`direct_raw`** | 0.2052 | 0.2121 | 0.2145 | **0.2106 $\pm$ 0.0039** |
| **`direct_unit_norm`** | 0.2052 | 0.2121 | 0.2145 | **0.2106 $\pm$ 0.0039** |
| **`projected_direct`** | 0.1986 | 0.2041 | 0.2067 | **0.2031 $\pm$ 0.0034** |
| **`projected_direct_delay`** | 0.2024 | 0.2052 | 0.2080 | **0.2052 $\pm$ 0.0023** |

*Nota:* Piso empírico basal (chute proporcional à macro-prevalência de 21 tags) = **0.176**. As baselines diretas mostram sinal semântico mensurável estável acima do piso.

### Operadores Recorrentes em Andamento:
- O processo atual está computando a simulação de reservatório do **`malecns` (Seed 0)** em 7 ganhos.
- Os estados computados ficam em cache em `artifacts/runtime-v1/state-cache/` e os resultados parciais em `artifacts/runtime-v1/multieurlex-exp1-results.partial.json`.

---

## 4. Como Continuar em Outro Computador

### Passo 1: Clonar e Sincronizar
```bash
git clone https://github.com/franklinbaldo/papers.git
cd papers
git checkout feature/algorithmic-connectome-paper
git pull origin feature/algorithmic-connectome-paper
```

### Passo 2: Entrar no Ambiente do Experimento
```bash
cd experiments/malecns_wifi
# Assegurar dependências instaladas via uv
uv sync
```

### Passo 3: Dados de Entrada
Se o arquivo `artifacts/runtime-v1/multieurlex-1000-features.npz` já estiver presente ou transferido, o runner executa direto. Caso a máquina não tenha o arquivo gerado localmente, ele é baixado e construído em ~30s via o Hugging Face cache (`franklinbaldo/multieurlex21-pt-semantic-cache`). O script verifica e retoma automaticamente de qualquer checkpoint `.partial.json`.

### Passo 4: Executar o Runner Congelado
```bash
uv run python scripts/run_multieurlex_exp1.py \
  --seeds 0 1 2 \
  --operators malecns rewired_p10 rewired_p50 degree_null
```
O script possui tolerância a falhas:
- Se encontrar `multieurlex-exp1-results.partial.json`, ele lê o `config_hash` (`51a18753d30bbd4f6e76`) e **não recalcula as células já prontas**.
- Continua imediatamente a partir da célula em aberto.

### Passo 5: Critérios de Decisão a Registrar nos Resultados
Ao finalizar e gerar `artifacts/runtime-v1/multieurlex-exp1-results.json`:
1. Calcular $\Delta_{\text{null-bio}} = AP_{\text{degree-null}} - AP_{\text{MaleCNS}}$.
2. Verificar monotonicidade ao longo do continuum de rewiring: $p=0.00 \to p=0.10 \to p=0.50 \to p=1.00$.
3. Se $\Delta > 0$ consistente com relaxamento gradual, registrar a confirmação em escala do gargalo biológico na Seção 3 e 8.1 do Paper 1.
