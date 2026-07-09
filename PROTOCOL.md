# Protocolo do aparato de debate adversarial/supportivo/síntese

**Versão 1** (2026-07-09). Consolida em um único documento regras que,
até esta data, só existiam reconstituídas a partir da prosa de 55
sessões de `synthesis/blog/`. Não substitui julgamento de síntese —
formaliza o que a prática já vinha fazendo, mais as duas correções
adotadas nesta revisão.

**Nota de escopo:** este arquivo descreve o protocolo pretendido para
o programa. Se as sessões automatizadas que executam os papéis
adversarial/supportivo/síntese são invocadas por um prompt ou rotina
externos a este repositório, elas só passarão a seguir este documento
se esse prompt for atualizado para referenciá-lo explicitamente.

## Papéis

- **`otherwise/`** — ataques adversariais a teses específicas dos
  papers principais. Um arquivo vivo por frente de debate (ex.:
  `otherwise/paper1c-formalization-tractability.md`), mais um
  changelog datado por sessão em `otherwise/blog/`.
- **`yesindeed/`** — defesas supportivas, mesma estrutura.
- **`synthesis/`** — árbitro. Funde PRs abertos pelos outros dois
  papéis e, periodicamente, roda um "ciclo de edição" que absorve
  conclusões assentadas de volta aos papers principais no nível
  superior do repositório. É o único papel que edita os papers
  principais.

## Gatilho de absorção (regra revisada)

**Regra anterior (sessões 1–55):** ciclo de edição fixo a cada 7
sessões de síntese (sessões 7, 14, 21, 28, 35, 42, 49; próximo: 56).

**Problema observado:** a própria sessão 28 diagnosticou que "the
cadence creates no pressure toward resolution that the debates
haven't already created themselves" — 2 dos 7 ciclos completados até
a sessão 55 não absorveram nada (no-op), e três frentes com concessão
bilateral explícita (paper1B, paper1C, paper1F) ficaram sem qualquer
absorção por múltiplos ciclos consecutivos, mesmo após ambos os lados
concederem pontos específicos.

**Regra revisada:** quando o "state assessment" de qualquer sessão de
síntese registra concessão bilateral explícita sobre um ponto
específico (linguagem do tipo "aceito", "concedido", "this defense
accepts", "ambos os lados concordam"), esse ponto entra na fila de
absorção imediata — não espera o próximo múltiplo de 7. O ciclo fixo
de 7 sessões permanece como binário de segurança complementar (garante
uma varredura completa mesmo quando nenhuma concessão pontual foi
sinalizada isoladamente), não como gatilho exclusivo.

**Não pausar a abertura de novas rodadas.** A regra acima resolve o
gargalo de absorção sem exigir pausa nas frentes ativas — pausar
desperdiçaria o momentum de debates em andamento sem necessidade
correspondente.

## Corte de debates em loop

Debates que se arrastam sem argumento novo são um risco documentado
(uma lacuna de citação em Paper 1B persistiu 16 sessões antes de
resolvida; ESHTR C2 teve um prazo formal perdido na sessão 46).
**Regra:** se uma rodada apenas reafirma posição anterior sem
argumento, fonte ou distinção nova, a síntese registra explicitamente
"sem avanço" nessa rodada; após duas rodadas consecutivas nessa
condição, a síntese força um veredito de fechamento — tipicamente
"posições interpretativas divergentes, sem fonte primária que resolva
a questão" — em vez de manter a frente aberta indefinidamente. O
veredito de fechamento não impede reabertura futura caso surja
argumento ou fonte genuinamente nova.

## Janela "ao vivo" e obrigações em atraso

Uma obrigação pendente (ex.: "supportivo deve responder rodada N")
sinalizada em um "state assessment" e não cumprida em 3 sessões passa
a "atrasada" no ledger da sessão seguinte. Após 3 sessões adicionais
sem resposta, a síntese trata o silêncio como concessão tácita
("silêncio = default do lado silencioso") e registra o ponto como
resolvido nesse sentido, sujeito a reabertura se o lado silencioso
retomar a frente.

## Cobertura

Antes de abrir uma nova frente adversarial ou supportiva, verificar se
algum dos 17 papers principais nunca teve nenhuma frente aberta contra
si (lista mantida em `propostas_melhoria_2026-07-09.md`, Nível 2). Não
há obrigação de cobrir todos — mas a ausência de cobertura não deve
ser presumida como sinal de qualidade: os dois achados de integridade
mais sérios encontrados na revisão de 2026-07-09 estavam exatamente
nos dois papers (`paper5_empirical_evaluation.md`,
`paper6_sintese.md`) que nunca haviam sido examinados por nenhuma
frente.
