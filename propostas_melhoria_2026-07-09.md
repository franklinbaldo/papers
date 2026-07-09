# Propostas de melhoria — auditoria do programa de pesquisa

**Data:** 2026-07-09
**Escopo:** os 17 papers de nível superior deste repositório e o aparato de debate automatizado (`otherwise/`, `yesindeed/`, `synthesis/`) que vem rodando desde 2026-05-13 (55 sessões de síntese até a data deste documento).
**Método:** três auditorias independentes (processo/cobertura da rotina; série dogmática 1A–1G; papers técnicos e corpus sem cobertura), com verificação manual direta dos achados mais graves antes de entrarem aqui. Não é uma sessão de síntese da rotina — é uma revisão externa complementar a ela.

---

## Diagnóstico geral

Dois problemas estruturais, independentes entre si:

1. **Gargalo de absorção.** `otherwise/` + `synthesis/` + `yesindeed/` somam ≈491 mil palavras em ~150 arquivos; os 17 papers somam ≈65 mil palavras. Só 7 "edit cycles" (a cada 7 sessões) já rodaram, e **2 dos 7 (29%) não absorveram nada** (no-op). Pior: **paper1B, paper1C, paper1F e o paper1_dogmatico (guarda-chuva da série) nunca foram editados desde o commit inicial** — apesar de o debate já estar em 10, 9 e 4 rodadas, respectivamente, com pontos que os dois lados já concederam explicitamente. O trabalho intelectual mais caro do programa está represado nos satélites e não chega ao produto final.
2. **Problemas de integridade encontrados por leitura direta, não pelo debate.** A rotina adversarial/supportiva é extremamente minuciosa dentro dos temas que escolhe atacar — mas 9 dos 17 papers nunca foram alvo de nenhum arquivo em `otherwise/` ou `yesindeed/`, e mesmo dentro dos papers cobertos, ela deixou passar defeitos básicos (autocontradição interna, citação que diz o oposto do que é citada para sustentar, uma "avaliação de originalidade" que é a saída colada de uma sessão de navegação do ChatGPT). Nenhum desses achados abaixo depende de julgamento sobre o mérito jurídico ou técnico — são inconsistências verificáveis no próprio texto.

As seções abaixo estão em ordem de prioridade. Nenhuma edição foi aplicada — isto é uma proposta para sua decisão sobre o quê e em que ordem.

---

## Nível 0 — Integridade (maior prioridade; risco reputacional se publicado como está)

Cada item abaixo foi conferido diretamente nos arquivos, com número de linha.

### 0.1 — `paper5_empirical_evaluation.md`: o paper afirma ter resultados que não tem

- Abstract (linha 29): encerra corretamente com "*results section to be completed upon data collection*".
- **Introdução, linhas 42–44** contradiz o próprio abstract duas linhas depois de citá-lo: "*This paper closes the empirical loop: it applies the methods to real Brazilian judicial decisions **and reports quantitative results**.*" — falso como está escrito.
- §3 "Results" é integralmente rotulado "Expected Output" (design pré-registrado, sem coleta de dados).
- §6 (Conclusão) volta a admitir corretamente: "*results will be added upon data collection*".
- Diferente de ESHTR, STT e Pontifex, este paper **não tem o banner `> **Position paper.**`** que os outros três usam para avisar o leitor de que não há resultados medidos.
- O README.md herda o exagero: "avaliação empírica em corpus do TJRO".
- **Proposta:** adicionar o banner de position paper (mesmo padrão de ESHTR/STT/Pontifex) logo após o título; corrigir a linha 42–44 para o mesmo tom hedged do abstract e da conclusão; ajustar a linha do README.

### 0.2 — `paper6_sintese.md`: erro de aritmética na própria contagem do programa

- Resumo, linha 11–12: "composto por **sete** papers".
- Mesmo resumo, decompõe em: eixo dogmático = "**seis** papers" + eixo metodológico-formal = "**três** papers" + eixo empírico = "**um** paper".
- 6 + 3 + 1 = **10**, não 7. A lista de Referências do próprio paper6 (linhas 338–351) tem exatamente 10 itens, confirmando 10.
- **Causa raiz provável:** o §2 "eixo dogmático" nomeia só 1A–1F e nunca menciona o **paper1G** (690 linhas, presente no repo, listado no README) — daí o "seis" em vez de "sete" nesse eixo, e o total desalinhado.
- Além disso, paper6 **nunca menciona** STT, Pontifex, o3-originality ou `paper_affordance_restriction.md` — 3 dos 5 eixos que o próprio README.md declara. Um paper que se autodescreve como "síntese do programa de pesquisa" cobre 2 eixos e meio de 5.
- **Proposta:** corrigir a contagem, incluir paper1G no §2, e decidir explicitamente se os eixos de alignment/interpretabilidade entram na síntese ou se o escopo do paper6 é redefinido (e anunciado) como parcial.

### 0.3 — `o3-orinality-assessement.md`: não é uma avaliação independente

Citado duas vezes por `pontifex_position_paper.md` (§2.4, §8) como se fosse checagem externa de originalidade/estado da arte. Evidência de que é, na verdade, a saída colada de uma sessão de navegação de um modelo (o próprio nome do arquivo já entrega o autor: "o3-"):

- As 3 URLs de rodapé têm `?utm_source=chatgpt.com` — parâmetro de rastreamento que a ferramenta de busca do ChatGPT anexa aos resultados.
- Linha 14: "*the central claim documented in **the uploaded draft and implementation guide***" — referência a arquivos que não existem neste repositório (ficaram órfãos de uma sessão de chat onde o usuário tinha "subido" um PDF).
- Linha 30: "*(example in the PDF)*" — mesmo problema.
- Linha 41: cita "novelty scoring frameworks (e.g. **TRL §12.2**)" sem definir o que é — TRL normalmente significa *Technology Readiness Level*, não um framework de originalidade, e nenhum framework desse tipo é definido em lugar nenhum do repositório.
- Veredito genérico e afirmativo ("Pontifex is genuinely new" / "Original enough to publish") — exatamente o formato que se obtém pedindo a um chatbot para validar a própria ideia, sem nenhuma ressalva sobre a superficialidade da própria busca que descreve ("A survey across arXiv, ACL Anthology, CVPR, and GitHub turned up no architecture..." — afirmado, não documentado).
- **Proposta:** ou (a) remover o arquivo e as duas citações em Pontifex, deixando claro que a checagem de originalidade ainda está pendente; ou (b) reclassificar o arquivo explicitamente como "prompt exploratório, não avaliação independente" e não usá-lo como evidência de ineditismo. Renomear o arquivo por si só (corrigindo os dois erros de digitação "orinality"/"assessement") não resolve o problema de fundo.

### 0.4 — STT: Apêndice B contradiz o próprio banner do paper

- Linhas 9–12: "*> **Position paper.** ... **No empirical results are reported.** Sequence-length, fidelity, and downstream-task figures appear only as design targets and falsifiable predictions, not as measurements.*"
- Linhas 1144–1159, **Apêndice B ("Hyperparameter Tuning Results")**: duas tabelas com números específicos — Perplexity, BLEU-4, OER, Entropy, Training Time — incluindo uma linha em **negrito** marcada como "melhor" combinação (chunk 192/stride 128 → 8.2x / 24.3 / 68.9 / 4.2%), sem seção de metodologia, sem contagem de execuções, sem barras de erro, sem qualquer referência cruzada em §5 (protocolo de avaliação) ou §8 (conclusão).
- Nem `otherwise/stt-retrieval-hallucination.md` nem `yesindeed/stt-corpus-scope-defense.md` menciona o Apêndice B, apesar de ambos discutirem em profundidade praticamente todo o resto do paper — a rotina adversarial simplesmente não olhou para lá.
- **Proposta:** ou remover/mover o Apêndice B para um repositório de resultados futuros com metodologia documentada, ou adicionar uma nota explícita classificando esses números como projeções/metas de design (consistente com o banner) em vez de resultados medidos.

### 0.5 — ESHTR §4: citação que sustenta o oposto do que é citada para sustentar

- Linhas 374–377: "*Bradley-Terry aggregation provides robustness for non-directional residual cycling that does not correlate systematically with item identities (`otherwise/eshtr-phase3-gap.md` §3.3–3.4; `yesindeed/frame-stability-sph.md` §3.4).*"
- As seções citadas do lado adversarial têm títulos que já denunciam o problema: **"§3.3 Item-Level Criterion Activation *Defeats* the Aggregation Defense"** e **"§3.4 The Operationalization: Best Available Does Not Mean Sufficient"**. O conteúdo de §3.3 mostra que, para itens com perfil "cross-strength", a ativação de critério é **sistemática** (não não-direcional) na maioria dos pareamentos — exatamente a premissa que a robustez do Bradley-Terry precisa negar. §3.4 conclui literalmente: "*whether within-cluster cycling is systematic or non-systematic **cannot be determined** from the experimental output the current protocol design produces.*"
- Ou seja: o texto principal do ESHTR cita uma seção de ataque ainda não resolvida — cujo autor mesmo diz que a questão está em aberto — como se ela desse suporte à alegação de robustez.
- **Proposta:** reformular a frase para refletir o estado real do debate (ex.: "sob a hipótese, ainda não estabelecida empiricamente, de que..."), ou mover a citação para a seção de limitações (§7.3), que já cita corretamente outras partes desse mesmo debate como pontos em aberto.

### 0.6 — Numeração fantasma "Paper 4"

`paper2_pipeline_lean_argdown.md` (§8, linha 619), `paper3_proveniencia_claims.md` e `paper5_empirical_evaluation.md` (abstract linha 13, intro linha 41) chamam o ESHTR de "**Paper 4** of this series" — mas nenhum arquivo `paper4_*` jamais existiu no repositório (confirmado em todo o histórico do git), e o próprio texto do ESHTR nunca se autodenomina "Paper 4". É uma numeração usada por terceiros que nunca foi formalizada nem no README nem no próprio ESHTR.
**Proposta:** decidir uma numeração canônica única (README já usa nomes de arquivo, não números — mais simples talvez seja parar de numerar e trocar as 4 ocorrências de "Paper 4"/"Paper 2"/"Paper 3" por nomes de arquivo ou títulos).

---

## Nível 1 — Backlog de absorção pronta (concedido pelos dois lados do debate; sem julgamento editorial necessário)

Estes pontos já são consenso entre `otherwise/` e `yesindeed/` — a rotina só não os escreveu de volta nos papers principais. São os candidatos de menor risco para incorporação imediata.

| Paper | O que já foi concedido por ambos os lados | Onde entraria |
|---|---|---|
| `paper1B_cinco_saidas_precedentes.md` | Decisões por "Saída 4" **nunca são efetivas** — sempre sujeitas a reforma, mesmo quando "corretamente" executadas (`otherwise/paper1b-rational-supersession.md` §3.1, aceito pela defesa) | §3.4/§3.5 |
| `paper1B_cinco_saidas_precedentes.md` | Saída 4 **não está disponível** para precedentes constitucionais vinculantes do STF (controle concentrado, súmulas vinculantes) — só no domínio infraconstitucional/STJ | §3.2/§3.4 ou §7 |
| `paper1B_cinco_saidas_precedentes.md` e `paper1_dogmatico_ED_precedentes.md` | A citação ao art. 927, §4º CPC como base do terceiro elemento cumulativo (§4.3 de 1B) foi **abandonada pela própria defesa** ("Art. 927, §4º is not part of this argument") depois que o ataque estabeleceu que o §4º trata de autorrevisão do tribunal de origem, não de afastamento por tribunal inferior | 1B §4.3; dogmático §3.3 |
| `paper1C_categorias_processuais_formalizacao.md` | A circularidade do pré-processamento **vale para formalizadores automatizados** — o abstract promete que "formalizadores humanos ou sistemas automatizados" podem implementar as categorias; isso já não é mais sustentado sem ressalva | Abstract; §5.4 |
| `paper1C_categorias_processuais_formalizacao.md` | A regra do "menor denominador comum" para ratio decidendi **falha** para decisões STF de maioria fragmentada/paralela (Mitidiero, Macêdo) — concedido pela defesa | §5.3 |
| `paper1E_custos_argumentativos.md` | O modelo de jogo 2×2 trata "o STF" como ator unitário quando na prática é o relator individual quem decide, com custo reputacional diluído entre 11 ministros — "genuine modeling gap", aceito pela própria defesa | novo item em §5.4, ao lado dos outros 4 limites já lá |
| `paper1F_reputacao_sistema_juridico.md` | O mecanismo só funciona claramente para violações identificáveis textualmente (omissão de precedente/dispositivo, inconsistência interna) e seu valor incremental se concentra em **dockets de alto volume e baixa revisão** — não é uma recalibração geral do sistema | Abstract; §4.1 |
| `paper1F_reputacao_sistema_juridico.md` | O canal de reputação é **local** (juiz-parte específico), não em rede — "the defense does not establish the full democratization prediction" | §4.1/§5.1 |
| `paper1F_reputacao_sistema_juridico.md` | O mecanismo de Kreps é estruturalmente perturbado no Brasil por **distribuição aleatória por sorteio**, **rodízio de vara/juiz** e **processamento mediado por assessores** — nenhum desses três termos aparece hoje no texto do paper | §4.3 |
| `paper1_dogmatico_ED_precedentes.md` | §2.2 ainda afirma a versão não-qualificada ("decorre automaticamente") de uma tese que `paper1A` já restringiu, após 10 rodadas de debate, aos casos em que o marco de comprometimentos do tribunal **determina univocamente** o desfecho | §2.2 |

Dois candidatos adicionais de baixíssimo risco (mecânicos, sem qualquer disputa de mérito):

- **`paper2_pipeline_lean_argdown.md`**: 13 marcadores `[CITE ...]` no corpo do texto (linhas 48–143) já têm entrada completa na própria lista de Referências (Dung, Cayrol/Lagasquie-Schiex, Bowers/Ludäscher, Han et al.) — é só converter `[CITE Dung 1995...]` em `(Dung, 1995)`.
- **`paper6_sintese.md`**: a descrição de 1B (§2.1) já bate com o abstract atual de 1B mesmo com todo o debate em curso — ou seja, nem tudo em paper6 está desatualizado, só a cobertura (quais papers existem), não necessariamente o conteúdo do que já cobre.

---

## Nível 2 — Papers com cobertura zero na rotina

Nenhum arquivo em `otherwise/` ou `yesindeed/` jamais foi aberto para os seguintes **9 de 17 papers** (confirmado por busca em todos os documentos vivos e blogs):

`paper1_dogmatico_ED_precedentes.md` (guarda-chuva) · `paper1G_livre_convencimento_patrimonialismo.md` · `paper2_pipeline_lean_argdown.md` · `paper3_proveniencia_claims.md` · `paper5_empirical_evaluation.md` · `paper6_sintese.md` · `paper_affordance_restriction.md` · `pontifex_position_paper.md` · `o3-orinality-assessement.md`

Dois casos merecem destaque:

- **`paper1G`** é o único paper lettered (1A–1G) sem nenhum debate — e, como mostra o Nível 0.2, é justamente o que ficou de fora da contagem do paper6. Ele também **assume como resolvidos** mecanismos de 1E e 1F (§1, §4.4, §6.3: "o Paper 1F demonstrou que...", "pressão... de três lados") que, pela Nível 1 acima, são na verdade bem mais restritos do que 1G pressupõe. Quando 1E/1F absorverem as ressalvas do Nível 1, 1G precisará de ajuste em cadeia — vale sinalizar isso já, mesmo sem abrir um debate formal para 1G.
- **`paper5` e `paper6`** — justamente os dois com os problemas de integridade mais sérios (Nível 0.1 e 0.2) — nunca tiveram um único parágrafo escrutinado adversarialmente. Não é coincidência: a rotina só encontra o que decide atacar.

**Proposta:** não necessariamente abrir debate formal de 55 rodadas para os 9 — seria caro e o Nível 3 já recomenda desacelerar a abertura de novas frentes. Mas pelo menos uma passada de revisão de qualidade (mesmo que manual, fora do aparato adversarial) antes de qualquer divulgação externa desses 9, dado que 2 meses de rotina não geraram nenhum escrutínio sobre eles.

---

## Nível 3 — Processo/arquitetura da própria rotina

Achados extraídos das próprias sessões de síntese (a rotina já se autodiagnostica bem; o problema é que os diagnósticos não viram ação):

- **Cadência fixa de 7 sessões não é o mecanismo certo para decidir quando absorver.** A própria sessão 28 (`synthesis/blog/2026-06-10-session-28-edit-cycle-4-no-op-double-reprieve.md`) já registrou: *"the edit cycle structure is not the governing mechanism for when absorptions happen... the cadence creates no pressure toward resolution that the debates haven't already created themselves."* Isso bate com o achado do Nível 1: pontos já concedidos há semanas continuam fora dos papers porque não coincidiram com um dos 7 ciclos. **Proposta:** disparar absorção assim que um "state assessment" registra concessão bilateral, em vez de esperar o próximo múltiplo de 7.
- **Debates que se arrastam sem critério de corte.** Exemplo citado pela própria rotina: uma lacuna de citação em Paper 1B persistiu **16 sessões** antes de ser resolvida (`synthesis/blog/2026-06-20-session-38...md`: "11 sessions of failure suggests it may not exist in the form either routine has been searching for"); ESHTR C2 teve um prazo formal perdido ("**TERMINAL MISSED**", sessão 46). **Proposta:** regra explícita de corte — se N rodadas não produzem argumento novo, força-se um veredito de síntese (ex.: "posições interpretativas divergentes, sem fonte primária que resolva") em vez de mais uma rodada.
- **Não existe nenhum documento de regras.** As regras reais (cadência de 7, janela de "ao vivo" de 3 sessões, mecânica de prazo terminal) só existem espalhadas em prosa nos 55 posts de blog — não há `PROTOCOL.md`/`RULES.md`/`CLAUDE.md` em lugar nenhum do repositório. **Proposta:** consolidar isso em um arquivo canônico curto.
- **README.md desatualizado em dois pontos concretos:** (a) a seção "## Log" ainda aponta para `session_log.md`, que tem exatamente 2 entradas, ambas de 2026-05-12 — nunca mais atualizado depois que `synthesis/blog/` assumiu esse papel no dia seguinte; (b) a seção "Companion pieces" descreve `otherwise/` e `yesindeed/` mas **nunca menciona `synthesis/`**, que é o papel que de fato edita os papers principais.
- **Há 3 PRs abertos agora mesmo** (#174 síntese sessão 55, #175 Paper 1B round 11 adversarial, #176 ESHTR C2 round 12 supportivo) abrindo/avançando rodadas novas em 1B e ESHTR-C2 — exatamente as duas frentes com o maior backlog não absorvido (Nível 1). **Proposta a considerar:** pausar a abertura de rodadas novas em 1B/1C/1F até uma passada de absorção dedicada, em vez de deixar o backlog crescer enquanto o debate segue.

---

## Nível 4 — Higiene rápida (mecânico, baixo risco)

- Renomear `o3-orinality-assessement.md` (dois erros de digitação) — mas só faz sentido depois de decidir o destino do conteúdo (ver 0.3).
- Renomear `semantic_tokenization_transformers (1).md` → `semantic_tokenization_transformers.md` (o "(1)" é resíduo de download duplicado) e atualizar a referência no README.
- Preencher ou marcar formalmente os placeholders `[DATA]`/`[VEÍCULO]`/`[LINK]`/`[CITE]` ainda abertos no rodapé de praticamente todos os 8 papers da série dogmática mais paper2/3/5/6.

---

## Como posso ajudar a partir daqui

Não apliquei nenhuma dessas mudanças — este documento é a proposta. Posso executar, mediante sua confirmação de escopo:

1. **Nível 0** isoladamente (6 correções pontuais, texto já redigido acima para cada uma) — risco mais baixo apesar do nome, porque são inconsistências objetivas no próprio texto, não decisões de mérito.
2. **Nível 1** (absorção do que os dois lados do debate já concederam) — recomendo priorizar 1B e 1C, que são os que mais debate acumularam sem nenhuma edição desde o commit inicial.
3. **Nível 3** (README, doc de protocolo, mudança de cadência) — mudanças de processo, não de conteúdo.
4. **Nível 4** — mecânico, posso fazer junto com qualquer um dos anteriores.

Me diga quais níveis (ou itens específicos) você quer que eu execute agora.
