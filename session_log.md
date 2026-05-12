# Log de Sessões de Melhoria Incremental

Cada entrada registra: data, frente atacada, resultado (commit/PR ou skip), e fila visível para próxima sessão.

---

## 2026-05-12 — Sessão 1

**Frente:** Integridade epistêmica — referências do paper ESHTR.

**Contexto:** Sessão anterior (PR #3) havia convertido o ESHTR de paper empírico para position paper, substituindo `[CITE ...]` por IDs arXiv e marcando entradas da lista de referências com `†` (não confirmadas). O STT foi reframado com predições falsificáveis.

**Trabalho desta sessão:** Verificação independente das referências marcadas com `†`.

**Resultados da verificação:**

| Referência | arXiv/Venue | Resultado |
|---|---|---|
| Knockout Assessment | arXiv:2506.03785 | ✓ Confirmado — Sandan, Dinh, Niehues. GEM@ACL 2025. |
| Non-Transitivity LLM Judge | arXiv:2502.14074 | ✓ Confirmado — Xu, Ruis, Rocktäschel, Kirk. ICML 2025 Spotlight. |
| COURTREASONER | EMNLP 2025 | ✓ Confirmado — Han et al. (10 autores). |
| Neveditsin et al. | arXiv:2511.19350 | ✓ Confirmado — Neveditsin, Lingras, Mago. Título completo inclui "with a Cohesion-Based Evaluation Metric". |
| Judge-Aware Ranking | arXiv:2601.21817 | ✓ Confirmado — Xu, Tan, Wu, Zhou. Submetido jan/2026 (year era incorretamente "2025"). |
| UDA | arXiv:2508.09724 | ✓ Autores confirmados — Zhang et al. (7 autores). Venue "AAAI 2026" **não confirmada** — mantida como preprint. |
| Bowers & Ludäscher | CEUR Vol-4157 | Não verificado. Mantido com †. |
| Raju et al. 2024 | arXiv 2024 | Não verificado. Título e autores completos não confirmados. Mantido com †. |

**Mudanças commitadas:**
- Inline: `(arXiv:2506.03785, 2025)` → `(Sandan et al., 2025)` (2 ocorrências)
- Inline: `(arXiv:2502.14074, 2025)` → `(Xu et al., 2025)` (2 ocorrências — texto e teoria)
- Lista de referências: 6 entradas `†` substituídas por entradas completas verificadas
- Lista de referências: 2 entradas mantidas com `†` (Bowers & Ludäscher, Raju et al.)
- Nota prefatorial da seção de referências atualizada para refletir estado atual

**PR:** [a criar]

**Fila para próxima sessão:**
1. Verificar Bowers & Ludäscher (2025) CEUR Vol-4157 — existe o volume?
2. Identificar Raju et al. (2024) — encontrar paper exato sobre stratified sampling para LLM evaluation diversity.
3. Identificar survey de biases em LLM judges ("[CITE survey 2025]" foi removido do texto pela sessão anterior, mas a referência bibliográfica correspondente nunca foi adicionada — o texto agora lista os três biases sem citar nenhuma fonte específica).
4. Verificar se a venue AAAI 2026 do UDA foi confirmada subsequentemente.
5. STT: as predições P1–P6 estão sem referência cruzada com o método descrito no Seção 3 — verificar consistência.
