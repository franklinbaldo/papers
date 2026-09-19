---
type: "Dogmatic Paper"
title: "Custos Argumentativos e Precedentes no Brasil: IA, qualidade auditável e pressão institucional como hipótese de equilíbrio"
description: "Modelo conceitual do canal brasileiro em que redução do custo de produzir argumentos auditáveis pode alterar a interação entre litigantes, órgãos inferiores e STF, condicionado por qualidade, cabimento processual e custos de triagem."
tags: [paper1e, precedentes, custos-argumentativos, law-and-economics, inteligencia-artificial, reclamacao, stf, cpc]
timestamp: 2026-07-09T12:12:59+00:00
authors:
  - ref: /authors/franklin-silveira-baldo.md
    byline: "Franklin Silveira Baldo"
    affiliations:
      - "Independent Researcher"
    corresponding: true
publication:
  status: ready
  targets: [zenodo]
  zenodo:
    publication_type: preprint
    access_right: open
    license: cc-by-nc-4.0
    version: "0.1"
---

# Custos Argumentativos e Precedentes no Brasil: IA, qualidade auditável e pressão institucional como hipótese de equilíbrio

**Franklin Silveira Baldo**  
Independent Researcher

> **Nota de escopo e prioridade.** Esta versão incorpora a auditoria temporal de prior art de 18 de setembro de 2026. Não reivindica novidade para divergência entre incentivos privados e sociais na litigância, interação estratégica entre cortes superiores e inferiores, efeitos de custos de litigância sobre evolução jurídica, nem ganhos de produtividade jurídica associados à IA generativa. A contribuição residual é mais estreita e específica ao arranjo brasileiro: a hipótese de que **redução do custo de produzir argumentos de alta qualidade e auditáveis**, combinada com deveres de fundamentação do CPC 2015 e com canais processualmente disponíveis de engajamento do STF, pode alterar incentivos de produção, seleção e resposta a argumentos. O mecanismo compete com um canal oposto: custos menores podem aumentar volume, ruído e custo de triagem sem melhorar a qualidade institucional.

## Resumo

A literatura de law and economics há décadas estuda divergências entre incentivos privados e sociais à litigância, investimento na produção de precedentes e seleção evolutiva de regras jurídicas. A literatura de hierarquia judicial também modela estrategicamente relações entre cortes superiores e inferiores, e trabalhos anteriores a este paper já mostravam que sistemas de IA podem reduzir tempo e custo de tarefas jurídicas. Em particular, Thompson (2024) já conecta IA generativa, menor custo de serviços jurídicos, maior uso dos tribunais e aceleração potencial da mudança jurídica. Este artigo não reivindica esses componentes. Sua hipótese é mais localizada: no sistema brasileiro de precedentes, a redução do custo de produzir **argumentos juridicamente auditáveis e de qualidade**, quando esses argumentos alcançam o STF por um canal processualmente apropriado — como a reclamação no domínio em que ela é cabível —, pode aumentar o custo institucional de respostas que não enfrentem pontos materiais e modificar o equilíbrio de investimento argumentativo. O efeito não decorre automaticamente de “mais petições”. Custos menores também podem produzir volume de baixa qualidade, elevar custos de triagem e reduzir a probabilidade de engajamento. Por isso, a variável causal relevante proposta não é volume textual, mas uma conjunção mensurável de **qualidade/auditabilidade do argumento, acesso ao canal institucional e engajamento observável da corte**. O paper apresenta um modelo qualitativo, explicita o limite de competência entre crítica inferior e revisão formal de precedente e formula predições falsificáveis para futura avaliação empírica.

**Palavras-chave:** precedentes vinculantes; custos de litigância; teoria dos jogos; inteligência artificial; argumentação jurídica; reclamação; STF; CPC 2015; fundamentação; equilíbrio institucional.

## Abstract

Law-and-economics research has long examined divergences between private and social incentives to litigate, investment in precedent production, and the evolutionary selection of legal rules. Judicial-hierarchy research has likewise modeled higher and lower courts strategically, while pre-cutoff empirical work already showed that generative AI can reduce the time and cost of legal tasks. Thompson (2024), in particular, directly connects generative AI, lower legal-service costs, greater court use, and potentially faster legal change. This paper does not claim those ingredients as novel. Its narrower hypothesis concerns the Brazilian precedent system: reducing the cost of producing **high-quality, auditable legal arguments**, when those arguments reach the STF through a procedurally available channel such as a legally proper constitutional complaint, may increase the institutional cost of non-engagement and change incentives for argumentative investment. The effect does not follow automatically from higher filing volume. Lower drafting costs may instead generate low-quality volume, raise screening costs, and reduce engagement. The proposed causal variable is therefore not text quantity but a measurable conjunction of **argument quality/auditability, access to an institutional channel, and observable court engagement**. The paper presents a qualitative model, preserves the competence boundary between lower-court criticism and formal precedent revision, and formulates falsifiable predictions for future empirical evaluation.

**Keywords:** binding precedent; litigation costs; game theory; artificial intelligence; legal argument; constitutional complaint; Brazilian Supreme Court; judicial reasoning.

---

## 1. Introdução

A hipótese de que custos jurídicos afetam o comportamento dos agentes e a evolução do direito não é nova. Galanter mostrou como diferenças de recursos e capacidade de repetição alteram a posição estratégica dos litigantes; Landes e Posner trataram precedentes como estoque produzido por investimento; Rubin e Priest modelaram a relação entre incentivos à litigância e seleção de regras; Shavell examinou diretamente a divergência entre incentivo privado e incentivo social para litigar em um sistema custoso.

Também não é nova a modelagem estratégica da hierarquia judicial. Cameron, Segal e Songer, e depois Westerland e coautores, analisaram cortes superiores e inferiores como atores estratégicos sob mecanismos de revisão, sinalização, compliance e defiance.

A novidade tampouco está na proposição de que IA generativa pode reduzir custo de trabalho jurídico. Estudos experimentais anteriores ao corte deste paper documentaram ganhos de velocidade em tarefas de advocacia e, em determinados arranjos, preservação ou melhoria de qualidade. Thompson (2024) foi ainda mais próximo da formulação ampla de versões anteriores deste artigo: tratou IA como tecnologia que reduz custo marginal de serviços jurídicos e de preparação de argumentos, aumenta demanda por tribunais e pode acelerar mudança legal.

O problema interessante remanescente é mais específico.

O sistema brasileiro combina: (a) precedentes e enunciados com diferentes graus de força; (b) deveres explícitos de fundamentação, incluindo identificação de fundamentos determinantes e justificação de aplicação ou afastamento; (c) canais processuais de revisão e controle cujo cabimento varia conforme o tipo de precedente; e (d) uma crescente redução tecnológica do custo de pesquisa, triagem, redação e auditoria de material jurídico.

Este paper pergunta se essa combinação cria um canal institucional próprio. Em vez de sustentar que “IA barata produz mais argumentos e portanto melhora o direito”, formula-se hipótese condicional:

> **Quando a redução de custo aumenta a oferta de argumentos de alta qualidade e auditáveis, e esses argumentos conseguem alcançar o órgão competente por canal processualmente adequado, a probabilidade e o custo institucional de engajamento podem mudar.**

Essa formulação contém três filtros — qualidade, canal e resposta — que versões anteriores não separavam de modo suficiente.

---

## 2. O que já estava ocupado antes deste paper

### 2.1 Custos privados, custos sociais e produção de regras

A literatura econômica já fornece a estrutura básica para compreender por que investimento individual em litígio ou produção de informação jurídica pode divergir do que seria socialmente desejável.

Shavell mostra que o incentivo privado para demandar não coincide necessariamente com o incentivo social quando custos e benefícios externos não são internalizados. Landes e Posner tratam precedentes como capital jurídico cuja produção e substituição exigem investimento. Rubin e Priest ligam incentivos de litigância à seleção e evolução das regras.

A conclusão para este artigo é negativa e útil: não há contribuição original em dizer apenas que “produzir melhor direito custa e os benefícios podem ser difusos”.

### 2.2 Estratégia entre cortes superiores e inferiores

A interação estratégica vertical também é antecedente consolidado. Modelos de revisão, auditoria, compliance e defiance já representam cortes como agentes que antecipam o comportamento umas das outras.

O modelo qualitativo deste paper não deve, portanto, ser apresentado como descoberta da teoria dos jogos aplicada à hierarquia judicial. Seu valor potencial está no objeto específico da variável de esforço — **qualidade/auditabilidade argumentativa** — e na ligação proposta com a arquitetura brasileira de fundamentação e canais de controle.

### 2.3 Precedentes vinculantes e custos de litigância no Brasil

Rodrigues Neto (2017) já aplica raciocínio econômico a precedentes vinculantes brasileiros e custos de litigância. Embora o mecanismo e a direção examinados sejam diferentes, a combinação `precedente brasileiro + incentivos/custos` também não é espaço vazio.

### 2.4 IA e redução de custo jurídico

Choi, Monahan e Schwarcz; Nielsen e coautores; Chien e Kim; e trabalhos posteriores ao longo de 2024–2026 documentam produtividade jurídica assistida por IA em diferentes tarefas e condições.

Thompson (2024) é o antecedente mais próximo da proposição genérica que versões anteriores deste paper chamavam de contribuição central. Seu argumento conecta explicitamente IA generativa, redução de custos de pesquisa, escrita e construção argumentativa, maior uso do sistema judicial e potencial aceleração de mudança jurídica.

Por isso, a comparação estática genérica

\[
\text{custo jurídico menor} \Rightarrow \text{mais atividade jurídica / mudança mais rápida}
\]

é tratada aqui como antecedente, não como resultado deste paper.

---

## 3. O mecanismo brasileiro residual

### 3.1 Três variáveis, não uma

Seja um argumento jurídico produzido por um agente em um caso relacionado a precedente relevante. Para fins conceituais, definem-se três variáveis:

- \(Q\): qualidade/auditabilidade do argumento;
- \(A\): probabilidade de o argumento alcançar um canal processualmente adequado e sobreviver aos filtros de admissibilidade/seleção;
- \(E\): grau de engajamento observável da corte competente com o conteúdo material do argumento.

A redução tecnológica do custo de produção, \(C\), interessa apenas na medida em que modifica essas variáveis.

O mecanismo proposto não é

\[
C \downarrow \Rightarrow \text{qualidade institucional} \uparrow.
\]

A hipótese é condicional:

\[
C \downarrow \land Q \uparrow \land A>0
\Rightarrow
\Pr(E>0) \text{ pode aumentar},
\]

sob instituições em que argumentos materiais gerem dever ou incentivo de resposta.

Mesmo essa relação é uma hipótese, não um resultado empírico deste paper.

### 3.2 Qualidade auditável

“Qualidade” não significa estilo, extensão ou confiança retórica. Um argumento auditável deve permitir reconstrução de pelo menos:

1. fonte normativa ou precedente invocado;
2. proposição jurídica relevante;
3. fatos ou características do caso que ativam a proposição;
4. distinções ou conflitos alegados;
5. autoridade e competência institucional envolvidas;
6. conclusão que efetivamente decorre das premissas;
7. proveniência das citações e possibilidade de verificação externa.

IA pode reduzir o custo de produzir texto sem reduzir, na mesma proporção, o custo de satisfazer esses requisitos. O paper, portanto, separa **custo textual** de **custo analítico/verificacional**.

### 3.3 O canal processual importa

Um argumento excelente que não chega ao órgão competente ou chega por mecanismo incabível não produz o feedback institucional descrito aqui.

No domínio STF + súmula vinculante, a reclamação pode, quando processualmente cabível, levar ao Supremo uma controvérsia sobre aplicação, distinção ou aderência ao enunciado. Mas esse mecanismo não deve ser generalizado automaticamente a todos os precedentes do art. 927. O regime varia por tipo de precedente e corte.

A arquitetura jurídica deste paper acompanha a formulação competência-sensível do Paper 1D: órgão inferior pode aplicar, distinguir, criticar, sinalizar ou usar formas juridicamente reconhecidas de não aplicação concreta; **revisão/cancelamento formal** permanece com a autoridade e o procedimento competentes.

### 3.4 O custo de não engajamento

A hipótese específica é que argumentos auditáveis, concentrando fontes, distinções e implicações de maneira verificável, podem tornar mais visível o custo de uma resposta que ignore questão material.

Esse custo pode assumir formas diferentes:

- maior facilidade de apontar ausência de enfrentamento em recurso subsequente;
- maior exposição reputacional de inconsistência decisória;
- necessidade de produzir resposta institucional mais específica;
- maior facilidade de comparação entre casos semelhantes;
- geração de registros estruturados úteis para futura revisão do precedente.

Nada disso garante mudança de resultado. “Engajamento” é um endpoint distinto de “acolhimento”. A hipótese é que o sistema passa a responder de maneira diferente ao argumento; não que o argumento barato necessariamente vença.

---

## 4. Modelo qualitativo de equilíbrio

### 4.1 Estratégias

Para simplificar, considere dois polos institucionais.

O polo produtor — litigantes e órgãos que formulam razões — escolhe entre:

- **L:** produção de baixo investimento, difícil auditoria ou baixa especificidade;
- **H:** argumento de maior qualidade/auditabilidade, com custo maior.

O polo decisor escolhe entre:

- **R:** resposta de baixo investimento, suficiente para resolver o caso sem engajamento detalhado;
- **G:** engajamento analítico com o argumento material.

O paper não afirma que o sistema real possui apenas quatro estados. A matriz é uma redução conceitual para descrever incentivos.

### 4.2 Redução de custo não basta

Se tecnologia reduz o custo de H, mais agentes podem produzi-lo. Mas isso só desloca o comportamento institucional se outros parâmetros também mudarem.

Se o canal A é quase zero — por inadmissibilidade, filtragem ou falta de competência —, produzir H continua tendo pouco efeito institucional.

Se o decisor recebe enorme volume de H apenas aparente, com baixa verificabilidade real, o custo de triagem pode aumentar e tornar G menos provável.

Se, ao contrário, H é auditável e permite triagem barata, comparação estruturada e identificação objetiva dos pontos que exigem resposta, o custo marginal de G pode cair ou o custo de R pode subir.

Assim, o parâmetro relevante não é “quantos textos são produzidos”, mas a relação entre:

\[
\text{ganho de auditabilidade}
\quad\text{e}\quad
\text{custo adicional de triagem}.
\]

### 4.3 Dois canais concorrentes

A redução do custo argumentativo gera pelo menos dois canais.

**Canal construtivo:**

\[
C \downarrow
\to Q_{auditável} \uparrow
\to A \uparrow
\to \text{questões materiais mais verificáveis}
\to E \uparrow.
\]

**Canal de congestão:**

\[
C \downarrow
\to \text{volume} \uparrow
\to \text{ruído / duplicação / erro} \uparrow
\to \text{triagem} \uparrow
\to E \downarrow \text{ ou permanece constante}.
\]

A tese empírica futura depende de qual canal domina e em quais classes de processo.

---

## 5. Predições falsificáveis

Uma vantagem da formulação estreita é que ela produz observáveis distintos.

### P1 — produtividade sem qualidade não confirma o mecanismo

Se IA reduz tempo de redação e aumenta número de peças, mas não melhora verificabilidade, precisão de citações ou estrutura lógica, isso confirma apenas produtividade genérica — já coberta pelo prior art —, não o mecanismo C5+C6.

### P2 — qualidade sem acesso institucional também não basta

Se argumentos auditáveis são produzidos, mas não passam pelos filtros processuais ou não chegam à corte competente, a hipótese de feedback institucional não recebe suporte.

### P3 — engajamento deve ser medido separadamente do resultado

O endpoint primário adequado é mudança na qualidade/especificidade da resposta institucional a questões materiais comparáveis, não apenas taxa de vitória do litigante.

Possíveis métricas incluem:

- proporção de argumentos materialmente distintos expressamente enfrentados;
- precisão da identificação da tese/ratio relevante;
- número de pontos auditáveis respondidos versus ignorados;
- uso de distinção explícita;
- tempo/custo de triagem até identificar os pontos centrais;
- necessidade de correção posterior por citação inexistente, falsa premissa ou argumento duplicado.

### P4 — o canal de congestão pode dominar

Se o uso de IA eleva volume de petições ou extensão textual, aumenta erros e tempo de triagem e não melhora engajamento, a versão otimista do mecanismo é falsificada naquele regime.

### P5 — efeitos devem variar por desenho processual

O efeito esperado é maior onde há canal claro para o argumento chegar ao órgão competente e menor onde o mecanismo processual é estreito, inexistente ou inadequado. Uma estimativa agregada de “efeito da IA no Judiciário” pode esconder essas diferenças.

---

## 6. Relação com competência e precedentes vinculantes

Versões anteriores deste paper descreviam órgãos inferiores como capazes de “superar racionalmente” um precedente vinculante sempre que oferecessem razões fortes. Essa formulação não é mantida.

A produção de argumento crítico e sua qualidade são distintas da competência para alterar formalmente a fonte vinculante.

O órgão inferior pode, conforme o regime aplicável:

- aplicar o precedente;
- distinguir o caso;
- registrar crítica ou sinalização;
- apontar transformação normativa relevante;
- utilizar técnica de não aplicação concreta reconhecida pelo ordenamento;
- preservar a questão para recurso ou reclamação cabível.

Revisão, cancelamento ou substituição formal do precedente dependem da autoridade e do procedimento competentes. A hipótese econômica deste paper funciona sem conceder ao órgão inferior um poder institucional que ele não possua: basta que argumentos possam circular e receber resposta por canais legítimos.

---

## 7. Prior art e limite da contribuição

A auditoria temporal altera de modo substancial a alegação de contribuição.

**Galanter (1974)** ocupa a relação entre recursos, repeat players e capacidade de influenciar desenvolvimento jurídico.

**Landes & Posner (1976), Rubin (1977), Priest (1977) e Shavell (1981/1982)** ocupam partes centrais do arcabouço de investimento, seleção de regras e divergência entre incentivos privados e sociais.

**Cameron, Segal & Songer (2000) e Westerland et al. (2010)** ocupam o uso de modelos estratégicos na hierarquia judicial.

**Rodrigues Neto (2017)** já conecta precedentes vinculantes brasileiros e incentivos/custos de litigância.

**Choi, Monahan & Schwarcz; Nielsen et al.; Chien & Kim** ocupam o canal genérico de produtividade jurídica assistida por IA.

**Thompson (2024)** é o antecedente genérico mais próximo: IA generativa reduz custo de trabalho jurídico/litigância, aumenta demanda por tribunais e pode acelerar evolução do direito.

Diante disso, o paper não reivindica C1–C4 como componentes novos. Sua contribuição candidata é somente a conjunção C5+C6:

> redução do custo de **argumento auditável de alta qualidade** → acesso a canal brasileiro de controle/engajamento → alteração mensurável da resposta institucional sob deveres de fundamentação, com competência de revisão preservada.

Mesmo essa conjunção é apresentada como hipótese de framework, não como fato empírico estabelecido nem como reivindicação de prioridade exaustiva.

---

## 8. Limitações

Este paper não apresenta evidência empírica de mudança de equilíbrio no Judiciário brasileiro.

A matriz de estratégias é qualitativa e não estima payoffs reais. “Custo institucional” não é uma variável diretamente observada nesta versão e precisa ser operacionalizado antes de teste quantitativo.

Produtividade jurídica assistida por IA é heterogênea por modelo, tarefa, experiência do usuário e mecanismo de verificação. Ganhos de velocidade não implicam automaticamente ganho de qualidade.

O mecanismo depende de auditabilidade. Sistemas que produzem citações falsas, raciocínio difícil de verificar ou grande volume redundante podem piorar, não melhorar, o ambiente informacional.

O canal processual também é heterogêneo. Reclamação não é veículo universal de controle de toda categoria de precedente. O paper não generaliza sua hipótese institucional para todos os pronunciamentos vinculantes sem análise própria de cabimento e competência.

Finalmente, mudança na resposta judicial não implica melhora normativa. Mais engajamento pode produzir decisão mais explícita sem produzir direito substantivamente melhor. Qualidade argumentativa, engajamento e correção normativa devem ser avaliados separadamente.

---

## 9. Conclusão

A redução tecnológica do custo de trabalho jurídico é real e já foi objeto de literatura anterior; a relação entre custos de litigância e evolução jurídica também é antiga. O ponto que permanece interessante é institucionalmente mais estreito.

No sistema brasileiro, tecnologia pode alterar o custo de produzir argumentos suficientemente estruturados para serem auditados e comparados. Quando esses argumentos alcançam a autoridade competente por canal processualmente adequado, podem modificar a economia de atenção e resposta em torno de precedentes. Mas o mesmo choque tecnológico pode gerar congestionamento e ruído.

Por isso, a hipótese relevante não é “IA barata racionaliza o sistema”. É uma hipótese condicional e falsificável:

> **custos menores só sustentam melhora do circuito argumentativo quando reduzem o custo da qualidade verificável mais rápido do que aumentam o custo de triagem e quando existe um canal institucional capaz de transformar essa qualidade em engajamento.**

Esse recorte abandona uma reivindicação genérica de novidade e converte o paper em proposta testável sobre um mecanismo brasileiro específico.

---

## Referências

CAMERON, Charles M.; SEGAL, Jeffrey A.; SONGER, Donald. **Strategic Auditing in a Political Hierarchy: An Informational Model of the Supreme Court's Certiorari Decisions.** American Political Science Review, 2000.

CHIEN, Colleen V.; KIM, Miriam. **Generative AI and Legal Aid: Results from a Field Study and 100 Use Cases to Bridge the Access to Justice Gap.** Preliminary public draft, 2024; later Loyola of Los Angeles Law Review, v. 57.

CHOI, Jonathan H.; MONAHAN, Amy B.; SCHWARCZ, Daniel. **Lawyering in the Age of Artificial Intelligence.** Minnesota Law Review, v. 109, 2024.

GALANTER, Marc. **Why the ‘Haves’ Come Out Ahead: Speculations on the Limits of Legal Change.** Law & Society Review, v. 9, n. 1, 1974. DOI: 10.2307/3053023.

LANDES, William M.; POSNER, Richard A. **Legal Precedent: A Theoretical and Empirical Analysis.** NBER Working Paper 0146 / Journal of Law and Economics, 1976. DOI: 10.3386/w0146.

NIELSEN, Aileen; SKYLAKI, Stavroula; NORKUTE, Milda; STREMITZER, Alexander. **Building a better lawyer: Experimental evidence that artificial intelligence can increase legal work efficiency.** Journal of Empirical Legal Studies, 2024. DOI: 10.1111/jels.12396.

PRIEST, George L. **The Common Law Process and the Selection of Efficient Rules.** Journal of Legal Studies, v. 6, n. 1, 1977.

RODRIGUES NETO, João Máximo. **A Relevância dos Precedentes na Análise Econômica da Litigância — Um Estudo de Law and Finance.** Revista Direito em Debate, v. 26, n. 48, 2017. DOI: 10.21527/2176-6622.2017.48.63-83.

RUBIN, Paul H. **Why Is the Common Law Efficient?** Journal of Legal Studies, v. 6, n. 1, 1977. DOI: 10.1086/467562.

SHAVELL, Steven. **The Social versus the Private Incentive to Bring Suit in a Costly Legal System.** NBER Working Paper 0741, 1981; Journal of Legal Studies, 1982.

THOMPSON, Henry A. **AI and the law.** arXiv:2412.05090, v1, 6 dez. 2024.

WESTERLAND, Chad; SEGAL, Jeffrey A.; EPSTEIN, Lee; CAMERON, Charles M.; COMPARATO, Scott. **Strategic Defiance and Compliance in the U.S. Courts of Appeals.** American Journal of Political Science, v. 54, n. 4, 2010.

BRASIL. **Lei nº 13.105, de 16 de março de 2015 — Código de Processo Civil.** Texto compilado. <https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm>.

### Registro de auditoria de prioridade

A decomposição de claims, os cutoffs públicos, as buscas e classificações que limitam a contribuição desta versão estão preservados em `audits/prior-art/argumentative-costs-precedent-equilibrium-2026-09-18.md`. O registro é parte da proveniência do preprint e não substitui as fontes externas citadas acima.
