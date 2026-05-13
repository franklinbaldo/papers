# Raciocínio Jurídico Auditável: síntese de um programa de pesquisa

**Franklin Silveira Baldo**
Procurador do Estado de Rondônia (OAB/RO 5733)
Porto Velho, RO

---

## Resumo

Este artigo sintetiza o programa de pesquisa "Raciocínio Jurídico
Auditável", composto por sete papers publicados em série. O programa
tem três eixos: (i) eixo dogmático — seis papers sobre direito
processual civil brasileiro que estabelecem as categorias, distinções
e regras que o sistema de fundamentação e o regime de precedentes
do CPC 2015 exigem; (ii) eixo metodológico-formal — três papers
em inglês que desenvolvem o pipeline de formalização em Lean 4 com
Argdown, o framework de avaliação por painel de LLMs (ESHTR), e
o módulo de proveniência de claims; (iii) eixo empírico — um paper
com avaliação quantitativa em corpus real do TJRO. O artigo demonstra
a coerência interna do programa: os papers dogmáticos são a
especificação formal dos módulos Lean; os papers técnicos são a
implementação dessas especificações; e a hipótese central que une
os dois eixos é que a redução do custo de produção de argumentos
jurídicos auditáveis — tecnológica em sua forma, mas processual
em suas consequências — altera os incentivos do sistema de precedentes
em direção ao equilíbrio de diálogo racional que o CPC 2015 prescreve
e que a teoria reputacional do campo jurídico permitia identificar
como o equilíbrio bloqueado.

**Palavras-chave**: raciocínio jurídico; auditabilidade; precedentes;
Lean 4; teoria dos jogos; reputação; CPC 2015; inteligência
artificial; formalização jurídica.

---

## 1. O programa e sua estrutura

O programa de pesquisa "Raciocínio Jurídico Auditável" parte de
uma pergunta simples: como tornar o raciocínio jurídico — a peça,
o voto, o parecer — auditável de modo que suas premissas sejam
rastreáveis, suas inferências verificáveis, e suas lacunas
identificáveis?

A pergunta tem dois aspectos que os sete papers tratam em paralelo.
O aspecto dogmático: o que o sistema jurídico brasileiro exige,
com precisão especificável, que os operadores façam ao fundamentar
decisões e ao usar precedentes? O aspecto técnico: que ferramentas
permitem formalizar esses requisitos de modo computacionalmente
verificável?

Os dois aspectos são inseparáveis. A formalização técnica sem base
dogmática sólida produz axiomas que o tribunal repudiaria. A
dogmática sem formalização permanece dispersa em manuais que poucos
lerão antes de peticionar. O programa une os dois: os papers
dogmáticos são a especificação que os módulos Lean implementam; os
módulos Lean são a operacionalização computacional do que os papers
dogmáticos estabelecem.

---

## 2. O eixo dogmático

Os seis papers dogmáticos cobrem três camadas de crescente abstração.

### 2.1 A camada processual direta

**Paper 1A** estabelece que os Embargos de Declaração têm escopo
amplo — o vício é definido pelo modo (obscuridade, contradição,
omissão), não pelo objeto (processual ou meritório) — e que os
efeitos infringentes são consequência automática do acolhimento,
não pretensão autônoma. A fórmula "subsidiariamente requer
infringência" é dogmaticamente imprecisa e deve ser substituída.

**Paper 1B** estabelece as cinco saídas legítimas do tribunal diante
de precedente vinculante: aplicação correta, distinção fundamentada,
reconhecimento de superação superveniente, superação racional com
apontamento expresso de erro, e abstenção da invocação. A leitura
penta-partida reflete o caráter racional, não hierárquico, da
vinculação a precedente no CPC 2015. O vício de "aplicação parcial
silenciosa" — invocar o precedente para a porção favorável e ignorar
as ressalvas — é nomeado e conceitualizado.

### 2.2 A camada de especificação para formalização

**Paper 1C** mapeia sistematicamente as categorias processuais que
os módulos Lean precisam capturar: taxonomia de pedidos e suas
relações (simples, alternativa, subsidiária, sucessiva, prejudicial),
taxonomia de provimentos com os dez incisos do art. 485 e as
modalidades do art. 487, regras de composição do dispositivo, e
a distinção necessária/contingente para afirmações em qualquer
documento processual.

### 2.3 A camada de teoria do sistema

**Paper 1D** demonstra que o dever de fundamentação do art. 489,
§1º, é simétrico: aplica-se ao órgão que afasta o precedente e
ao STF que julga a reclamação. O STF que responde à reclamação
com mera reafirmação de autoridade — sem enfrentar as razões expostas
— viola o mesmo dispositivo que exige do órgão inferior fundamentação
do afastamento. A estrutura resultante é de diálogo institucional
racional: a reclamação é canal pelo qual argumentos que resistem
ao confronto alcançam o tribunal competente para revisar o
precedente.

**Paper 1E** demonstra que o equilíbrio atual de baixa qualidade
argumentativa é estável por razão de estrutura de incentivos: o
custo individual de produzir argumento de qualidade excede o
benefício esperado, ainda que o benefício coletivo do diálogo
racional seja muito maior. A redução tecnológica do custo de
produção de argumentos jurídicos de qualidade altera os parâmetros
do jogo e cria condições para movimento em direção ao equilíbrio
superior. O argumento independe de qualquer ferramenta específica.

**Paper 1F** demonstra que o sistema jurídico opera por rede de
reputação distribuída como substituto para a verificação direta
de qualidade argumentativa. A reputação rastreia proxies de qualidade
(afiliação institucional, histórico de vitórias, titulação, network)
em vez de qualidade diretamente. Os agentes com alto capital
reputacional têm interesse estrutural em manter a opacidade
argumentativa que torna a reputação necessária e valiosa. A
recalibração reputacional pela verificabilidade direta desvaloriza
proxies e abre novo canal de construção de reputação para agentes
antes excluídos do sistema.

### 2.4 A coerência do eixo dogmático

Os seis papers formam progressão coerente. 1A e 1B são contribuições
processuais com aplicação forense imediata — qualquer procurador
pode usar as formulações e a taxonomia das cinco saídas hoje. 1C
é especificação para formalização computacional — é o paper que
liga o eixo dogmático ao eixo técnico. 1D e 1E são teoria do
sistema — descrevem o que o sistema deveria ser e por que não é,
com prescritiva sobre como pode mudar. 1F é a dimensão sociológica
— como o campo jurídico como sistema reputacional amplifica os
problemas que 1D e 1E identificam e como a recalibração tecnológica
os perturbaria.

---

## 3. O eixo técnico

Os papers técnicos implementam as especificações do eixo dogmático
e desenvolvem a infraestrutura de avaliação.

**Paper 2** apresenta o pipeline de seis fases: Argdown
(decomposição argumentativa), Lean 4 (formalização), análise
jurídica subjetiva (ciclo iterativo), síntese resolutiva, e
tradução forense. O argumento central contra a literatura dominante:
verificação por compilação é mais adequada que verificação por
aciclicidade para raciocínio jurídico, porque sistemas jurídicos
têm estrutura kelseniana circular que requisitos de aciclicidade
não acomodam. O `#print axioms` do Lean é o mecanismo de auditoria:
cada teorema expõe o conjunto completo de pressupostos, tornando
a estrutura de dependências transparente e reproduzível.

**Paper 3** introduz a distinção necessária/contingente para
afirmações em qualquer documento processual e formaliza em Lean
4 através dos tipos `Proveniencia` e `StatusClaim`, ambos com
construtor `pendente`. O construtor `pendente` não é estado de
erro; é registro honesto do limite epistêmico do formalizador.
Teoremas que dependem de axiomas pendentes carregam essa incerteza
através do `#print axioms`.

**Paper 4** (ESHTR) introduz o método de avaliação: clustering
de decisões por similaridade semântica (embedding), ranking intra-
cluster por painel de LLMs, e torneio inter-cluster entre vencedores.
A hipótese da proximidade semântica — que a incidência de não-
transitividade em juízes-LLM correlaciona com a distância semântica
entre itens comparados — é a motivação teórica para o seeding por
embedding.

**Paper 5** fornece a avaliação empírica em corpus real do TJRO,
com três condições (pipeline, LLM-simples, LLM-elaborado), rubrica
de dois eixos (validade procedimental × persuasividade), e protocolo
de calibração. A divergência entre os dois eixos é o diagnóstico
central: peças com alta persuasividade e baixa validade são o
patologia COURTREASONER que métricas puras de persuasividade
perderiam.

---

## 4. A hipótese central que une os dois eixos

O argumento que conecta os eixos dogmático e técnico é este: a
redução do custo de produzir argumento jurídico auditável — custo
que os papers técnicos efetivamente reduzem, ao oferecer pipeline
que qualquer procurador pode usar — altera os incentivos que os
papers dogmáticos (1D, 1E, 1F) identificam como bloqueadores do
equilíbrio racional.

Mais precisamente:

O Paper 1D descreve o equilíbrio que o sistema deveria ter: diálogo
institucional racional, dever simétrico de fundamentação, STF
obrigado a enfrentar argumentos. O Paper 1E descreve por que não
tem: custo individual de produzir argumento de qualidade excede o
benefício esperado. O Paper 1F descreve o mecanismo de manutenção:
rede reputacional baseada em proxies de qualidade, com capital
reputacional institucional protegendo a opacidade argumentativa.

Os papers técnicos atacam o custo que o Paper 1E identifica como
barreira. O pipeline de seis fases com Lean 4 e Argdown reduz o
custo de produzir argumento com estrutura auditável. O `#print
axioms` reduz o custo de verificar a solidez do argumento. A
análise subjetiva da Fase 3 reduz o custo de avaliar se as premissas
do argumento são defensáveis.

Quando o custo cai, o equilíbrio de incentivos identificado no
Paper 1E se move. Quando o equilíbrio se move, os proxies
reputacionais identificados no Paper 1F perdem valor relativo.
Quando os proxies perdem valor, o canal de construção de reputação
baseada em qualidade verificável se abre.

A hipótese não é que a tecnologia resolverá o problema do sistema
de precedentes brasileiro. É que a tecnologia altera os parâmetros
do jogo de um modo que torna o equilíbrio superior — o diálogo
racional — mais acessível do que era.

---

## 5. Contribuições autônomas

O programa tem contribuições que se sustentam independentemente
da hipótese central.

**Contribuições com aplicação forense imediata:**

- As duas regras sobre Embargos de Declaração (Paper 1A):
  formulação correta dos pedidos em ED, escopo amplo dos vícios
- As cinco saídas legítimas diante de precedente vinculante (Paper
  1B): a taxonomia tem aplicação em qualquer peça que envolva
  precedentes do art. 927
- O vício de aplicação parcial silenciosa (Paper 1B): nome e
  fundamento normativo para vício comum e pouco teorizado
- O módulo canônico de categorias processuais (Paper 1C):
  especificação sistemática de pedidos, provimentos, pretensões
  recursais para qualquer processo de formalização

**Contribuições teóricas:**

- A simetria do dever de fundamentação (Paper 1D): que o STF está
  obrigado pelo art. 489, §1º, ao julgar reclamações, com as
  implicações para teoria do diálogo institucional
- A análise de equilíbrio do sistema de precedentes (Paper 1E):
  estrutura de incentivos, equilíbrio de Nash, mecanismo de
  mudança
- A dimensão reputacional do campo jurídico (Paper 1F): capital
  simbólico, opacidade argumentativa como interesse estrutural,
  recalibração pela verificabilidade

**Contribuições metodológicas:**

- O pipeline de seis fases com Lean 4 e Argdown (Paper 2): primeira
  aplicação ao processo civil brasileiro; argumento de compilação
  vs. aciclicidade; cinco saídas como teorema derivado
- A distinção necessária/contingente para qualquer documento
  processual (Paper 3): extensão da ratio/obiter além dos
  precedentes
- O método ESHTR (Paper 4): embedding-seeded hierarchical tournament
  ranking para avaliação de qualidade de decisões judiciais em
  corpus heterogêneo; hipótese da proximidade semântica
- A métrica de dois eixos (Paper 5): diagnóstico da patologia
  COURTREASONER como desvio entre validade procedimental e
  persuasividade

---

## 6. Agenda de pesquisa futura

O programa identifica linhas de extensão que este conjunto de
papers não cobre.

**Extensão do pipeline para outros recursos.** O pipeline foi
desenvolvido e validado para Embargos de Declaração. Recurso
Especial e Recurso Extraordinário têm pretensões recursais com
estrutura diferente (matéria infraconstitucional / constitucional,
prequestionamento, repercussão geral) que exigiriam módulos Lean
específicos. A extensão é natural mas exige trabalho dogmático
adicional.

**Modelagem completa do processo como sequência.** O Paper 1C
documenta explicitamente que modelagem de `PeticaoInicial`,
`Contestacao`, fases procedimentais e pressupostos processuais
está fora do escopo atual. É a extensão mais ambiciosa — e a que
produziria sistema de formalização mais completo.

**Validação do argumento de teoria dos jogos (Paper 1E).** O
argumento sobre mudança de equilíbrio pela redução de custos é
teórico. Validação empírica exigiria: (a) medição longitudinal
da taxa de afastamento fundamentado de precedentes vinculantes
em tribunais com e sem acesso a ferramentas de auxílio à
fundamentação; (b) análise de qualidade de reclamações ao STF
ao longo do tempo; (c) análise de respostas do STF a reclamações
com fundamentação qualificada vs. simples.

**Análise da rede reputacional (Paper 1F).** O Paper 1F propõe
análise empírica do campo jurídico como rede reputacional. Essa
análise exigiria: mapeamento de redes de citação entre decisões
e peças, análise de trajetórias institucionais de operadores
jurídicos, e correlação entre capital reputacional (proxies) e
qualidade argumentativa verificável.

---

## 7. Conclusão

O programa "Raciocínio Jurídico Auditável" propõe que a
auditabilidade do raciocínio jurídico — a rastreabilidade de
premissas, a verificabilidade de inferências, a identificabilidade
de lacunas — não é característica de luxo de sistemas jurídicos
avançados. É condição para que o sistema de precedentes funcione
como o CPC 2015 pressupõe que funcione: por diálogo racional entre
tribunais de diferentes instâncias, com dever simétrico de
fundamentação que se aplica ao tribunal que afasta o precedente e
ao tribunal que julga a reclamação.

A tecnologia que os papers técnicos desenvolvem — o pipeline de
Lean 4 com Argdown, a avaliação por painel de LLMs com ESHTR, a
distinção de proveniência de claims — reduz o custo de produzir
e verificar argumentação auditável. Essa redução de custos altera
os incentivos que mantêm o equilíbrio de baixa qualidade
argumentativa. E essa alteração de incentivos tem consequências
para a qualidade do sistema de precedentes que nenhuma reforma
normativa isolada poderia produzir.

O programa não é otimista sobre velocidade. Equilíbrios institucionais
são teimosos, capital reputacional é resistente à desvalorização,
e o STF tem incentivo para resistir a mudanças que aumentam seu
custo de enfrentar argumentos. Mas a direção do movimento é clara
— e a base dogmática e técnica para que o movimento aconteça está
aqui.

---

## Referências

*Remissão aos papers da série:*

- Paper 1A: Embargos de Declaração no CPC 2015
- Paper 1B: As cinco saídas legítimas diante de precedente vinculante
- Paper 1C: Categorias processuais civis para formalização
  computacional
- Paper 1D: Vinculação racional e diálogo institucional
- Paper 1E: Custos argumentativos e equilíbrio institucional
- Paper 1F: Reputação como mecanismo de coordenação
- Paper 2: Pipeline Lean 4 com Argdown (inglês)
- Paper 3: Proveniência de claims (inglês)
- Paper 4: ESHTR — Embedding-Seeded Hierarchical Tournament Ranking
  (inglês)
- Paper 5: Avaliação empírica em corpus TJRO (inglês)

---

*Artigo de síntese da série "Raciocínio Jurídico Auditável".
Versão de [DATA]. Implementação: franklinbaldo/skills.*
