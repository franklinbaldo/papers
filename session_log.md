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

**PR:** #4 (mergeada em 2026-05-12)

**Fila para próxima sessão:**
1. Verificar Bowers & Ludäscher (2025) CEUR Vol-4157 — existe o volume?
2. Identificar Raju et al. (2024) — encontrar paper exato sobre stratified sampling para LLM evaluation diversity.
3. ~~Identificar survey de biases em LLM judges~~ — **resolvido na Sessão 2** (ver abaixo).
4. Verificar se a venue AAAI 2026 do UDA foi confirmada subsequentemente.
5. STT: as predições P1–P6 estão sem referência cruzada com o método descrito no Seção 3 — verificar consistência.

---

## 2026-05-12 — Sessão 2

**Frente:** Integridade epistêmica — biases sem citação no ESHTR.

**Contexto:** Sessão 1 havia removido o marcador `[CITE survey 2025]` do parágrafo de biases (§2.1), mas não havia adicionado citação real. O texto listava positional bias, verbosity bias e self-preference bias sem nenhuma fonte.

**Trabalho desta sessão:** Identificar e adicionar a citação correta.

**Verificação:** Busca confirmou que Zheng et al. (2023) "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS 2023, arXiv:2306.05685) documenta explicitamente "position, verbosity, and self-enhancement biases." Paper já estava nas referências verificadas do ESHTR.

**Mudanças commitadas:**
- §2.1 (Bias and reliability): adicionado `(Zheng et al., 2023)` ao final da enumeração de biases; termo "self-preference" alinhado ao termo de Zheng et al. ("self-enhancement").
- §5.3 (Connection to known bias sources): substituído "documented in the LLM-as-judge bias literature" por `(Zheng et al., 2023)`.
- `session_log.md` atualizado.

**PR:** #5

**Fila para próxima sessão:**
1. Verificar Bowers & Ludäscher (2025) CEUR Vol-4157 — existe o volume CEUR?
2. Identificar Raju et al. (2024) — paper exato sobre stratified sampling para LLM evaluation.
3. Verificar venue AAAI 2026 do UDA (Zhang et al., arXiv:2508.09724).
4. STT: as predições P1–P6 estão sem referência cruzada com o método descrito na Seção 3 — verificar consistência interna.
