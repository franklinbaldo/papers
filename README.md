---
type: "Index"
title: "papers"
description: "Catalogo e guia de leitura dos papers deste repositorio e do aparato de debate que os acompanha."
timestamp: 2026-07-09T12:12:59+00:00
okf_version: "0.1"
---

# papers

Position papers and working drafts.

## Raciocínio Jurídico Auditável (CPC 2015) — série dogmática

- `paper1_dogmatico_ED_precedentes.md` — Embargos de Declaração e saídas legítimas diante de precedente vinculante (umbrella)
- `paper1A_embargos_declaracao.md` — escopo dos vícios e efeitos infringentes
- `paper1B_cinco_saidas_precedentes.md` — cinco saídas legítimas (art. 927 §1º c/c art. 489 §1º V–VI)
- `paper1C_categorias_processuais_formalizacao.md` — categorias processuais e formalização
- `paper1D_vinculacao_racional_dialogo_institucional.md` — vinculação racional e diálogo institucional
- `paper1E_custos_argumentativos.md` — custos argumentativos
- `paper1F_reputacao_sistema_juridico.md` — reputação no sistema jurídico
- `paper1G_livre_convencimento_patrimonialismo.md` — livre convencimento e patrimonialismo

## Eixo metodológico-formal

- `pipeline_lean_argdown.md` — pipeline em Lean 4 + Argdown para auditoria de raciocínio jurídico
- `proveniencia_claims.md` — proveniência de claims
- `embedding_seeded_tournament.md` — ESHTR: avaliação por painel de LLMs
- `semantic_tokenization_transformers.md` — STT (position paper)

## Eixo aprendizagem algorítmica / machine teaching

- `generative_machine_teaching.md` — previsão do próximo bit como tarefa primitiva; tokenização endógena, adaptativa ao contexto, com provas de montagem e currículos procedurais binários
- `informational_time.md` — tempo como concatenação: tokenização recursiva como representação adaptativa sobre o fluxo primitivo, simetria e profundidade causal informacional
- `informational_time_negentropy_clarifications.md` — máxima entropia relativa ao observador; separação entre flutuação, lei externa estruturada e reconhecimento relacional de agente
- `pedagogical_signal_extraction.md` — irregularidade estruturada e extração de invariantes preditivos; tokens como instrumentos internos, não como segmentação canônica

## Eixo descoberta por máquinas / epistemologia computacional

- `machine_discovery.md` — descoberta como transição certificada entre estados epistêmicos, com novidade relativa, proveniência auditável e expansão recursiva do currículo

## Eixo alignment / agent-bounding

- `affordance_restriction.md` — alignment by affordance restriction: padrão para agentes auditáveis em domínios delimitados (PINK como exemplo trabalhado)
- `interstitial_agent.md` — agência, persistência informacional e segurança end-to-end em cadeias de LLMs conectadas por transdutores aprendidos

## Eixo interpretabilidade

- `pontifex.md` — Pontifex: byte-level occlusion + convergência multi-espaço para interpretabilidade tokenizer-free e cross-modal (position paper)
- `o3-originality-assessment.md` — esboço exploratório (saída de sessão de IA) de checagem de prior art para o Pontifex; não é avaliação independente — ver nota editorial no início do arquivo

## Eixo empírico

- `empirical_evaluation.md` — desenho pré-registrado de avaliação empírica em corpus do TJRO (resultados ainda não coletados)

## Síntese

- `sintese_programa.md` — síntese do programa "Raciocínio Jurídico Auditável" (eixos dogmático + metodológico-formal + empírico, onze papers; não cobre os eixos de alignment e interpretabilidade abaixo, tratados como linha de pesquisa correlata mas distinta)

## Companion pieces

- `otherwise/` — argumentos adversariais
- `yesindeed/` — argumentos de suporte
- `synthesis/` — árbitro: funde `otherwise/`/`yesindeed/` e roda os ciclos de edição que absorvem conclusões assentadas de volta aos papers principais
- `PROTOCOL.md` — regras do aparato de debate acima (papéis, gatilho de absorção, corte de debates em loop)

## Log

- `synthesis/blog/` — registro corrente de sessões, um arquivo datado por sessão (ativo desde 2026-05-13)
- `session_log.md` — registro de duas sessões de verificação de referências em 2026-05-12, anterior ao mecanismo acima; mantido como histórico, não recebe novas entradas
- `propostas_melhoria_2026-07-09.md` — auditoria externa do programa e propostas de melhoria (2026-07-09)

## Formato dos documentos (OKF)

Todo arquivo `.md` deste repositório (exceto `okf/index.md`, reservado
por convenção) carrega front matter YAML com pelo menos um campo
`type`, conforme o [Open Knowledge Format](okf/SPEC.md) v0.1. Os
`type` usados aqui são um vocabulário fechado e documentado em
`okf/types/` (um arquivo por tipo — `Dogmatic Paper`, `Adversarial
Critique`, `Session Log Entry`, etc.); `okf/validate.py` roda em CI
a cada PR e falha se um documento não tiver front matter válido ou
usar um `type` não registrado. Comece por `okf/index.md` para a
lista completa de tipos e o que cada um exige.
