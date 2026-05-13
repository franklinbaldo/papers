# Categorias Processuais Civis para Formalização Computacional: Pedidos, Provimentos, Pretensões Recursais e Proveniência de Afirmações no CPC 2015

**Franklin Silveira Baldo**
Procurador do Estado de Rondônia (OAB/RO 5733)
Diretor da Procuradoria do Patrimônio Imobiliário — PGE-RO
Porto Velho, RO

---

## Resumo

O presente artigo mapeia sistematicamente as categorias do processo
civil brasileiro que são necessárias para a formalização computacional
de argumentos jurídicos em assistentes de prova e sistemas de
raciocínio jurídico automatizado. O mapeamento tem por objeto quatro
grupos de categorias: (i) pedidos — taxonomia, relações estruturais
entre pedidos cumulados, alternativos, subsidiários, sucessivos e
prejudiciais, e o princípio da congruência como limite do julgamento;
(ii) provimentos — taxonomia completa incluindo as modalidades de
extinção sem resolução de mérito (art. 485 do CPC), as modalidades
homologatórias (art. 487, II e III), e as regras de composição do
dispositivo quando há múltiplos pedidos com provimentos distintos;
(iii) pretensões recursais — o efeito devolutivo e seus limites, a
pretensão recursal como objeto distinto da pretensão original, e a
relação entre o objeto do recurso e as saídas legítimas diante de
precedente vinculante; (iv) proveniência de afirmações — a distinção
entre claims necessárias e contingentes em qualquer documento
processual, o mecanismo de propagação de claims contingentes entre
documentos sucessivos, e as consequências processuais da não
identificação desse fenômeno. O artigo não pretende contribuição
dogmática inovadora; pretende precisão descritiva suficiente para
que formalizadores — humanos ou sistemas automatizados — possam
implementar corretamente as categorias em linguagens formais sem
distorcer o sistema jurídico subjacente.

**Palavras-chave**: formalização jurídica; pedido; cumulação de
pedidos; provimento; dispositivo; efeito devolutivo; pretensão
recursal; ratio decidendi; obiter dictum; claims contingentes;
CPC 2015.

---

## Abstract

This article systematically maps the categories of Brazilian civil
procedure that are necessary for the computational formalization of
legal arguments in proof assistants and automated legal reasoning
systems. The mapping covers four groups of categories: (i) claims —
taxonomy, structural relations among cumulated, alternative,
subsidiary, successive and prejudicial claims, and the congruence
principle as limit of adjudication; (ii) dispositions — complete
taxonomy including modalities of dismissal without merit resolution
(art. 485 CPC), homologatory modalities (art. 487, II and III), and
composition rules for the dispositif when multiple claims receive
distinct dispositions; (iii) appellate claims — the devolutive
effect and its limits, the appellate claim as an object distinct
from the original claim, and the relation between the scope of
appeal and the legitimate responses to binding precedent; (iv)
claim provenance — the distinction between necessary and contingent
claims in any procedural document, the mechanism of propagation of
contingent claims across successive documents, and the procedural
consequences of failing to identify this phenomenon. The article
does not aim at innovative dogmatic contribution; it aims at
sufficient descriptive precision for formalizers — human or
automated — to correctly implement the categories in formal languages
without distorting the underlying legal system.

**Keywords**: legal formalization; claim; claim cumulation;
disposition; dispositif; devolutive effect; appellate claim; ratio
decidendi; obiter dictum; contingent claims; CPC 2015.

---

## 1. Introdução e propósito

O processo de formalização computacional de argumentos jurídicos
envolve, necessariamente, uma etapa de tradução: conceitos do direito
processual — pedido, provimento, dispositivo, efeito devolutivo,
ratio decidendi — precisam ser representados em tipos, predicados
e axiomas de uma linguagem formal. Essa tradução é transparente
quando os conceitos jurídicos têm estrutura precisa e bem delimitada;
é problemática quando os conceitos são usados com imprecisão na
doutrina e na prática, ou quando distinções relevantes para a
formalização existem implicitamente no sistema mas não são articuladas
de modo sistemático.

O presente artigo tem por objeto precisamente as categorias que
são mais frequentemente imprecisas na tradição dogmática brasileira
e que, por isso, geram dificuldades específicas para a formalização
computacional. Não é paper de contribuição dogmática inovadora no
sentido de propor categorias novas ou reinterpretar dispositivos de
modo inédito. É paper de mapeamento sistemático: dado o sistema
jurídico brasileiro, quais são as categorias, distinções e regras
que um formalizador precisa conhecer com precisão antes de postular
axiomas?

A relevância dessa precisão é direta. Um sistema de formalização
que não distingue pedido subsidiário de pedido alternativo postula
axiomas que implicam obrigações de julgamento que o processo não
tem. Um sistema que não distingue ratio decidendi de obiter dictum
trata como vinculante algo que não vincula. Um sistema que não
distingue claim necessária de claim contingente no documento de
origem não consegue rastrear a propagação de erros entre documentos
processuais. Em cada caso, a imprecisão dogmática se transmite à
formalização e produz teoremas incorretos — que compilam mas não
refletem o direito.

O artigo está organizado em quatro seções substantivas,
correspondendo a quatro grupos de módulos em sistemas de formalização
jurídica: pedidos (seção 2), provimentos (seção 3), pretensões
recursais (seção 4), e proveniência de afirmações (seção 5). Cada
seção segue a mesma estrutura: apresentação das categorias relevantes
com precisão suficiente para formalização; identificação das
distinções que a prática dogmática frequentemente obscurece;
e enunciação das regras que governam as relações entre as categorias.

---

## 2. Pedidos: estrutura e relações

### 2.1 O pedido como unidade de análise

O pedido é o objeto do processo — aquilo que o autor pede ao
Estado-juiz. O art. 322 do CPC estabelece que o pedido deve ser
certo e determinado, e o art. 324 exige que seja expresso, vedada
a interpretação extensiva ou restritiva. Essas exigências têm
consequência direta para a formalização: o pedido é um objeto
identificável, com limites definidos, que o juiz deve respeitar
ao julgar (princípio da congruência, art. 141 e art. 492).

Para fins de formalização, o pedido tem três componentes:

**Objeto imediato**: o tipo de tutela jurisdicional requerida —
declaração, constituição, condenação, mandamento, execução. O objeto
imediato define a espécie de provimento que o juiz pode proferir.

**Objeto mediato**: o bem da vida pretendido — a coisa, a quantia,
a situação jurídica. O objeto mediato define o conteúdo do
provimento.

**Causa de pedir**: os fatos e os fundamentos jurídicos que
sustentam o pedido. A causa de pedir delimita o thema decidendum
— o tribunal deve julgar dentro da causa de pedir deduzida, salvo
questões de ordem pública conhecíveis de ofício.

A tríade objeto imediato / objeto mediato / causa de pedir é
necessária para a formalização correta porque determina o que está
dentro e fora do objeto do processo — e, por consequência, o que
está dentro e fora do efeito devolutivo do recurso.

### 2.2 Relações estruturais entre pedidos

O art. 326 do CPC autoriza a formulação de mais de um pedido em
ordem subsidiária. O art. 327 autoriza a cumulação de pedidos. A
distinção entre as diferentes relações estruturais entre pedidos
é fundamental para a formalização porque cada relação gera
obrigações de julgamento distintas.

**Pedidos cumulados** são pedidos independentes entre si,
formulados conjuntamente. O juiz deve pronunciar-se sobre todos,
podendo acolher uns e rejeitar outros. O dispositivo de sentença
em processo com pedidos cumulados é composto de tantos
pronunciamentos quantos forem os pedidos. A procedência parcial
em processo com pedidos cumulados significa que alguns pedidos
foram acolhidos e outros não — não que um pedido foi acolhido em
parte.

Para a formalização, pedidos cumulados são objetos independentes
que compartilham o mesmo processo mas têm provimentos autônomos.
O resultado agregado do processo é função dos provimentos
individuais, não um provimento único sobre todos os pedidos.

**Pedidos alternativos** são pedidos formulados de modo que qualquer
um deles satisfaz a pretensão do autor. O art. 325 do CPC autoriza
a formulação de pedido alternativo quando, pela natureza da
obrigação, o devedor puder cumprir a prestação de mais de um modo.
A satisfação de qualquer dos modos alternativos extingue a
obrigação. Para a formalização, pedidos alternativos formam um
conjunto disjuntivo: o provimento é procedente se qualquer
membro do conjunto for realizado.

**Pedidos subsidiários** — ou em ordem de eventualidade — são
pedidos formulados de modo que o segundo só é examinado se o
primeiro for rejeitado. O art. 326 do CPC é a base normativa. Para
a formalização, a relação é condicional: o provimento sobre o
pedido subsidiário é condicionado à rejeição do principal. O juiz
que acolhe o pedido principal não examina o subsidiário — e não
pode fazê-lo sem violar o princípio da congruência.

Essa estrutura tem implicação importante para a formalização de
embargos de declaração e de recursos: o pedido subsidiário que
o autor formulou como alternativa ao principal não pode ser
deferido pelo tribunal como se fosse pretensão autônoma após o
acolhimento do principal. O provimento sobre o subsidiário
pressupõe a rejeição do principal.

**Pedidos sucessivos** são pedidos em que o segundo depende do
acolhimento do primeiro para ser examinado. Diferem dos
subsidiários porque a condição de exame do segundo é o acolhimento
— não a rejeição — do primeiro. Para a formalização, a relação
é de dependência positiva: o segundo pedido só entra no thema
decidendum se o primeiro for acolhido.

**Pedidos prejudiciais** são aqueles cuja decisão afeta logicamente
a decisão sobre outro pedido. Para a formalização, a relação de
prejudicialidade determina a ordem de julgamento e pode tornar
o segundo pedido logicamente prejudicado se o primeiro for
resolvido de determinado modo.

### 2.3 O princípio da congruência como limite

O art. 492 do CPC estabelece que "é vedado ao juiz proferir
decisão de natureza diversa da pedida, bem como condenar a parte
em quantidade superior ou em objeto diverso do que lhe foi
demandado". O princípio da congruência é o correlato normativo
da estrutura de pedidos: o juiz deve pronunciar-se sobre o que
foi pedido, nem mais nem menos.

Para a formalização, o princípio da congruência é uma restrição
sobre o espaço de provimentos legítimos: dado um conjunto de
pedidos com suas relações estruturais, os provimentos do juiz
devem corresponder exatamente a esse conjunto. Provimento sobre
objeto não pedido é ultra petita (vício); provimento sobre objeto
parcial do pedido pode ser infra petita (vício) ou parcialmente
procedente (legítimo), dependendo do caso.

A distinção entre infra petita e parcialmente procedente é
relevante para a formalização: infra petita é vício de omissão
— o juiz não se pronunciou sobre parte do pedido; parcialmente
procedente é resultado legítimo — o juiz se pronunciou sobre
todo o pedido e acolheu parte. Confundir os dois produz axiomas
incorretos sobre quando há omissão sanável por embargos.

---

## 3. Provimentos: taxonomia e composição do dispositivo

### 3.1 A distinção fundamental: com e sem resolução de mérito

O sistema de provimentos do CPC 2015 organiza-se em torno de
uma distinção fundamental: provimentos com resolução de mérito
(art. 487) e provimentos sem resolução de mérito (art. 485). Essa
distinção tem consequência sobre a coisa julgada material (que
só se forma nos provimentos com resolução de mérito) e sobre a
possibilidade de repropositura da ação.

Para a formalização, a distinção é necessária porque determina
o escopo da coisa julgada — que é, por sua vez, o que delimita
o objeto dos recursos e do pedido de cumprimento.

### 3.2 Provimentos sem resolução de mérito (art. 485)

O art. 485 do CPC lista as hipóteses de extinção do processo sem
resolução de mérito. Para a formalização, cada inciso tem condições
de aplicação distintas que precisam ser representadas com precisão:

**Inciso I — indeferimento da petição inicial**: aplicável quando
a petição inicial é inepta (art. 330), o autor for manifestamente
ilegítimo, ou o autor carecer de interesse processual. Condição:
defeito originário da petição inicial, detectável antes da citação
do réu.

**Inciso II — abandono do processo pelo autor**: o processo ficou
parado por mais de trinta dias por negligência do autor. Condição:
inércia do autor por prazo legal.

**Inciso III — abandono bilateral**: ambas as partes abandonaram
o processo. Condição: inércia de ambas as partes.

**Inciso IV — ausência de pressupostos processuais de constituição
e desenvolvimento válido**: o processo tem vício que impede seu
desenvolvimento. Para a formalização, os pressupostos processuais
são condições de validade do processo — petição inicial apta,
citação válida, capacidade das partes, competência do juízo.

**Inciso V — perempção, litispendência e coisa julgada**: a ação
não pode ser proposta porque o direito de propô-la foi extinto
(perempção), já existe ação idêntica em curso (litispendência),
ou a mesma questão já foi definitivamente decidida (coisa julgada).

**Inciso VI — ausência de condições da ação**: o autor é
manifestamente ilegítimo ou carece de interesse processual. Para
a formalização, as condições da ação são verificadas em relação
ao pedido tal como formulado — legitimidade ad causam é
correspondência entre o autor e o titular do direito afirmado,
e interesse processual é necessidade e utilidade da tutela
jurisdicional.

**Incisos VII, VIII e IX**: convenção de arbitragem, desistência
da ação, e morte de parte em ação personalíssima. Condições
específicas de cada hipótese.

**Inciso X**: casos previstos neste Código. Cláusula residual.

### 3.3 Provimentos com resolução de mérito (art. 487)

O art. 487 do CPC lista as hipóteses de resolução de mérito:

**Inciso I — acolhimento ou rejeição do pedido**: o provimento
ordinário. O juiz examina o pedido e o acolhe (procedente) ou
rejeita (improcedente). O acolhimento parcial é provimento
parcialmente procedente — o juiz acolhe parte do objeto mediato
do pedido. Para a formalização, a distinção entre procedente,
parcialmente procedente e improcedente é relevante porque
determina o objeto do recurso cabível e o que transita em julgado.

**Inciso II — decisão homologatória**: reconhecimento da ocorrência
de decadência ou prescrição, que extingue o direito com resolução
de mérito. Para a formalização, a diferença em relação à
decadência/prescrição reconhecida no art. 485, IV (que extingue
sem resolução de mérito) é que no art. 487, II, o juiz enfrenta
e resolve a questão de mérito da prescrição ou decadência.

**Inciso III — homologação de autocomposição**: homologação de
reconhecimento do pedido, de transação ou de renúncia ao direito
sobre o qual se funda a ação. Para a formalização, a homologação
de autocomposição é provimento com resolução de mérito que não
decorre do julgamento do mérito pelo juiz, mas da disposição das
partes — o juiz homologa, não decide.

### 3.4 Provimentos parciais e o art. 356

O art. 356 do CPC introduz a possibilidade de julgamento antecipado
parcial do mérito: o juiz pode decidir parcialmente o mérito quando
um ou mais pedidos forem incontroversos, estiverem em condição de
imediato julgamento, ou a parte for revel. O provimento parcial
antecipado transita em julgado imediatamente e pode ser executado
provisoriamente.

Para a formalização, o julgamento parcial antecipado significa que
o dispositivo final do processo pode ser resultado da composição
de provimentos proferidos em momentos distintos — o provimento
parcial antecipado do art. 356 e os provimentos sobre os pedidos
restantes na sentença final. A composição é necessária para
determinar o resultado agregado do processo.

### 3.5 Regras de composição do dispositivo

Quando o processo tem múltiplos pedidos com diferentes relações
estruturais e provimentos distintos, o resultado agregado —
o que normalmente se chama de "procedência total", "procedência
parcial" ou "improcedência" — é função da composição desses
provimentos segundo as relações estruturais entre os pedidos.

As regras de composição são:

Para **pedidos cumulados**: o resultado agregado é procedente
total se todos os pedidos forem acolhidos; improcedente total se
todos forem rejeitados; e parcialmente procedente em qualquer
outra combinação.

Para **pedidos subsidiários**: o resultado é determinado pelo
primeiro pedido acolhido na ordem de subsidiariedade. Se o
principal é acolhido, o resultado é procedente no principal (o
subsidiário não é examinado). Se o principal é rejeitado e o
subsidiário é acolhido, o resultado é procedente no subsidiário.
Se ambos são rejeitados, improcedente.

Para **pedidos alternativos**: o resultado é procedente se
qualquer dos pedidos alternativos for acolhido; improcedente se
todos forem rejeitados.

Para **pedidos sucessivos**: o resultado sobre o segundo pedido
só integra o dispositivo se o primeiro for acolhido. Se o primeiro
é rejeitado, o segundo é prejudicado — não é improcedente.

Para a formalização, a distinção entre prejudicado e improcedente
é relevante: pedido prejudicado não transitou em julgado (não
houve resolução de mérito); pedido improcedente sim. A diferença
determina se o pedido pode ser reproposto e qual o objeto do
recurso.

---

## 4. Pretensões recursais: objeto e limites

### 4.1 A pretensão recursal como objeto autônomo

O recurso não é apenas a continuação do processo em instância
superior; é meio de impugnação de decisão judicial com pretensão
própria que opera sobre o objeto do processo original, mas não se
confunde com ele.

A pretensão recursal tem dois componentes:

**Pedido recursal**: o que o recorrente pede ao tribunal ad quem
— reforma, anulação, integração (no caso dos embargos de
declaração). O pedido recursal delimita o que o tribunal pode
fazer: não pode reformar o que não foi pedido na apelação (ultra
petita recursal).

**Fundamentos recursais**: as razões pelas quais o recorrente
entende que o pedido recursal deve ser acolhido. Os fundamentos
recursais determinam o âmbito de cognição do tribunal — as
questões que o tribunal pode e deve examinar.

Para a formalização, a pretensão recursal é objeto distinto da
pretensão original: é necessário representar separadamente (a) o
que foi pedido na ação, (b) o que foi decidido na sentença, e (c)
o que está sendo pedido no recurso e por quais fundamentos.

### 4.2 O efeito devolutivo e seus limites

O efeito devolutivo é o efeito pelo qual o recurso transfere ao
tribunal ad quem o conhecimento das matérias impugnadas. O art.
1.013 do CPC disciplina o efeito devolutivo da apelação, e seu
§1º estabelece que "serão, porém, objeto de apreciação e julgamento
pelo tribunal todas as questões suscitadas e discutidas no processo,
ainda que não tenham sido solucionadas, desde que relativas ao
capítulo impugnado".

Para a formalização, o efeito devolutivo tem extensão e
profundidade:

**Extensão**: determinada pelo pedido recursal — o que foi
impugnado. O tribunal não pode conhecer de matéria não impugnada
(reformatio in pejus), com exceção das matérias de ordem pública
conhecíveis de ofício (art. 1.013, §3º).

**Profundidade**: determinada pelo thema decidendum do capítulo
impugnado — todas as questões suscitadas e discutidas relativamente
ao capítulo, mesmo as não decididas pelo juiz de primeiro grau.
O tribunal ad quem não está limitado à fundamentação da sentença;
pode examinar todas as questões que competia ao juiz examinar.

A distinção entre extensão e profundidade é necessária para a
formalização porque determina duas coisas distintas: o que o
tribunal pode reformar (extensão) e quais questões o tribunal
deve examinar ao julgar o que pode reformar (profundidade).

### 4.3 Pretensão recursal e saídas diante de precedente vinculante

A relação entre a pretensão recursal e o regime de precedentes
vinculantes tem implicação que merece atenção específica na
formalização.

Quando o tribunal ad quem invoca precedente vinculante como
fundamento para julgar o recurso, ele está exercendo a pretensão
de julgar o capítulo impugnado. O que o tribunal pode fazer com
o precedente — aplicar, distinguir, reconhecer superação
superveniente, superar racionalmente — é exatamente o espaço
das cinco saídas legítimas mapeadas no artigo da série dedicado
ao tema. Para a formalização, essa conexão significa que os
módulos de provimentos recursais precisam importar os módulos
de saídas legítimas: o provimento de um recurso que envolve
precedente vinculante é um par (provimento recursal, saída diante
do precedente).

Um acórdão que reforma a sentença por aplicação de precedente
vinculante precisa ter, na formalização, dois componentes: o
provimento recursal (reforma a sentença para julgar o pedido
improcedente, por exemplo) e a saída adotada em relação ao
precedente (aplicação correta, distinguishing, etc.). A ausência
de qualquer dos dois componentes é vício de fundamentação — que
é precisamente o tipo de vício que os sistemas de formalização
visam detectar.

### 4.4 Efeito translativo e matérias de ordem pública

O efeito translativo é a possibilidade de o tribunal conhecer,
de ofício, de matérias de ordem pública não alegadas pelo
recorrente. O art. 1.013, §3º, do CPC autoriza o tribunal a
julgar desde logo o mérito quando a causa estiver em condição de
imediato julgamento e houver reforma da sentença que extinguiu o
processo sem resolução do mérito, ou quando o processo contiver
questão exclusivamente de direito.

Para a formalização, o efeito translativo é exceção ao princípio
da congruência recursal: o tribunal pode pronunciar-se sobre
matéria não impugnada quando se tratar de ordem pública. As
matérias de ordem pública — pressupostos processuais, condições
da ação, matérias do art. 485 — são axiomas do sistema de
formalização que operam como exceções às regras gerais de
congruência.

---

## 5. Proveniência de afirmações: ratio, obiter e claims contingentes

### 5.1 O problema da propagação

Todo documento processual — petição inicial, contestação, sentença,
acórdão, precedente — produz afirmações que exercem funções
distintas no texto. Algumas afirmações são necessárias para o
efeito jurídico que o ato produz; outras são contingentes —
presentes no texto mas não necessárias para o efeito.

A distinção é relevante para a formalização porque claims
contingentes de documentos anteriores se propagam inadvertidamente
nos documentos posteriores. O juiz de segundo grau que constrói
sobre afirmação contingente da sentença de primeiro grau pode
estar expandindo o objeto do processo além do que foi efetivamente
decidido. O advogado que não identifica essa propagação não tem
como atacar o fundamento correto.

Para a formalização, cada afirmação extraída de um documento
processual precisa ser anotada com dois atributos: (a) sua
proveniência — de qual documento ela vem e com qual status
epistêmico a tomamos; e (b) seu status no documento de origem —
necessária ou contingente.

### 5.2 Claims necessárias e contingentes em cada tipo de ato

O critério de distinção entre claim necessária e contingente é
funcional: uma claim é necessária em um documento se, sem ela,
o efeito jurídico do ato não ocorreria ou seria substancialmente
diferente.

**Na petição inicial**: as causas de pedir são necessárias —
definem o thema decidendum. Argumentações de reforço, contexto
histórico, e fundamentos alternativos que o autor inclui por
precaução mas dos quais não depende o pedido são contingentes.
Para a formalização, apenas as causas de pedir vinculam o thema;
os argumentos contingentes podem ser considerados pelo juiz mas
não precisam ser enfrentados se o pedido puder ser resolvido pelas
causas de pedir necessárias.

**Na contestação**: a impugnação específica dos fatos (art. 341
do CPC) é necessária — a ausência de impugnação específica produz
confissão ficta dos fatos não impugnados. Argumentação meritória
que vai além da impugnação, fundamentos subsidiários, e
considerações de contexto são contingentes. Para a formalização,
a distinção entre impugnação necessária e argumentação contingente
determina o que precisa ser enfrentado na sentença sob pena de
omissão e o que pode ser ignorado sem vício.

**Na sentença**: o fundamento sem o qual o dispositivo não se
sustenta é necessário. Os fundamentos alternativos — "ainda que
assim não fosse, também se verificaria que..." —, as observações
de contexto, e os obiter dicta sobre questões não decididas são
contingentes. Para a formalização, apenas os fundamentos
necessários da sentença transitam em julgado nos limites do art.
504, II, do CPC; os contingentes não vinculam nem limitam o objeto
da apelação.

**No acórdão**: a estrutura é análoga à da sentença, com a
complicação adicional de votos concorrentes. Um voto concorrente
— que chega ao mesmo resultado por fundamento diferente — é, em
relação à ratio do acórdão, potencialmente contingente: se a
maioria não adotou aquele fundamento, ele não integra a ratio do
acórdão, ainda que conste do documento.

**No precedente vinculante**: a distinção entre ratio decidendi
e obiter dictum é a forma específica que a distinção
necessária/contingente assume nos precedentes. Ratio decidendi
é o fundamento necessário para a conclusão do precedente;
obiter dictum é o fundamento que estava presente no raciocínio
mas não era necessário para a conclusão.

### 5.3 A distinção ratio/obiter em profundidade

A distinção entre ratio decidendi e obiter dictum é um dos temas
mais trabalhados na teoria do precedente, mas menos precisamente
tratados na dogmática processual brasileira. Para a formalização,
precisão é necessária.

**Ratio decidendi** é o fundamento jurídico que foi determinante
para a conclusão do precedente — aquele sem o qual o precedente
não teria chegado ao resultado que chegou, aplicado aos fatos
relevantes do caso. A identificação da ratio não é leitura da
ementa nem do dispositivo; é análise de qual argumento foi
necessário e suficiente para a conclusão.

**Obiter dictum** é tudo que o tribunal disse além do necessário
para a conclusão. Inclui: fundamentos alternativos que poderiam
ter levado ao mesmo resultado mas não foram os adotados;
observações sobre questões não decididas; hipóteses sobre como
o tribunal decidiria em casos análogos; argumentos de reforço
que não eram necessários para a conclusão.

Para a formalização, apenas a ratio vincula. O obiter é
argumentativamente relevante — pode ser persuasivo, pode ser
citado, pode indicar a orientação do tribunal sobre questões
futuras — mas não tem o peso vinculante da ratio. Axioma postulado
com base em obiter de precedente vinculante tem grau de confiança
inferior a axioma postulado com base na ratio.

A identificação da ratio em precedentes brasileiros tem
complicação específica: o sistema de julgamento colegiado, com
votos individuais por ministro, pode produzir acórdãos em que
a maioria concorda no resultado mas não nos fundamentos. Nesses
casos, a ratio é o menor denominador comum dos fundamentos dos
votos que formam a maioria — o que todos os votos majoritários
têm em comum como fundamento necessário para o resultado. Os
fundamentos que cada ministro adicionou individualmente mas que
não foram compartilhados pelos demais são, em relação ao acórdão
como precedente, obiter.

### 5.4 Proveniência e status como atributos formais

Para a formalização computacional, cada afirmação usada como
axioma precisa carregar dois atributos:

**Proveniência**: de onde a afirmação vem. As categorias são:
(a) endógena — produzida pelo formalizador como axioma do sistema,
sem ancoragem em documento específico do processo; (b) fonte
declarada — o documento de destino cita explicitamente o documento
de origem; (c) fonte inferida — o formalizador infere que a
afirmação vem de documento anterior com base no contexto, sem
citação explícita; (d) confirmada pelo procurador — o formalizador
perguntou ao procurador que confirmou a origem; (e) pendente —
a proveniência não foi determinada e pode ou não ser determinável.

**Status no documento de origem**: (a) necessária — a afirmação
era fundamento necessário para o efeito do ato; (b) contingente
— a afirmação estava presente no documento mas não era necessária;
(c) pendente — o status não foi determinado.

Para a formalização, axiomas com proveniência inferida ou
pendente, ou com status contingente ou pendente, têm grau de
confiança inferior a axiomas com proveniência declarada ou
confirmada e status necessário. Essa hierarquia de confiança
não impede a formalização — não é necessário que todos os axiomas
sejam de alta confiança para que o trabalho avance —, mas precisa
ser registrada e comunicada ao usuário do sistema.

### 5.5 Mecanismo de propagação e suas consequências processuais

A propagação de claims contingentes entre documentos ocorre quando
o documento posterior trata como fundamento estabelecido algo que
era contingente no documento anterior. O mecanismo tem duas formas:

**Propagação por omissão de contestação**: a parte adversária não
contestou a afirmação contingente no recurso ou na contestação.
Afirmações não impugnadas em embargos de declaração, por exemplo,
são consideradas aceitas pela parte que não embargou. Se o tribunal
tratou afirmação contingente da sentença como estabelecida, e o
recorrente não a impugnou na apelação, ela pode transitar em
julgado como fundamento do acórdão — mesmo sendo contingente na
sentença original.

**Propagação por incorporação ativa**: o documento posterior
incorpora ativamente a afirmação contingente do anterior como
fundamento necessário do novo ato. O acórdão que diz "conforme
assentado na sentença de primeiro grau, [afirmação contingente]"
está tratando a afirmação contingente como fundamento necessário
da sentença — o que ela não era.

A consequência processual da identificação de propagação por
incorporação ativa é relevante: o recorrente que demonstra que o
acórdão está fundado em afirmação que era contingente na sentença
de primeiro grau pode argüir que o acórdão ampliou o objeto do
processo além do que foi efetivamente decidido — o que é vício
de ultra petita indireta, ou violação do efeito devolutivo.

Para a formalização, o rastreamento da propagação requer que o
sistema identifique, para cada axioma do acórdão, se ele era
necessário ou contingente no documento anterior que lhe serve de
fonte. Essa verificação retroativa — do documento disponível para
os documentos anteriores — é o mecanismo de inferência regressiva
que sistemas de formalização jurídica devem implementar.

---

## 6. Conclusão

O mapeamento realizado neste artigo tem propósito específico:
fornecer ao formalizador computacional — humano ou automatizado —
a precisão descritiva necessária para implementar corretamente as
categorias do processo civil brasileiro em linguagens formais.

As quatro áreas mapeadas — pedidos, provimentos, pretensões
recursais e proveniência de afirmações — são aquelas onde
imprecisão dogmática se transmite com maior facilidade à
formalização, produzindo axiomas incorretos que compilam mas não
refletem o direito.

Para pedidos: a distinção entre cumulados, alternativos,
subsidiários, sucessivos e prejudiciais não é meramente
terminológica — gera obrigações de julgamento distintas que
precisam ser representadas nas relações entre objetos formais.

Para provimentos: a distinção entre extinção com e sem resolução
de mérito, e as condições específicas de cada inciso do art. 485,
são necessárias para representar corretamente o que transita em
julgado e o que pode ser reproposto.

Para pretensões recursais: a pretensão recursal é objeto autônomo
com extensão e profundidade distintas; o efeito devolutivo delimita
o espaço de cognição do tribunal; e a relação entre a pretensão
recursal e as saídas diante de precedente vinculante é conexão
necessária entre os módulos de provimento e os módulos de
precedentes.

Para proveniência de afirmações: a distinção entre necessária
e contingente, aplicada a qualquer documento processual, é
condição para o rastreamento de propagação de erros entre
documentos. O atributo de proveniência (endógena, declarada,
inferida, confirmada, pendente) e o atributo de status
(necessária, contingente, pendente) devem integrar qualquer
axioma de fato em sistemas de formalização jurídica.

O presente artigo integra série de trabalhos sobre formalização
computacional de argumentos jurídicos brasileiros. Os papéis
anteriores da série examinam a natureza dos Embargos de Declaração
no CPC 2015 e as cinco saídas legítimas diante de precedente
vinculante. Os papéis subsequentes descrevem a arquitetura
técnica dos sistemas de formalização e os métodos de avaliação
empírica.

---

## Referências

ASSIS, Araken de. *Manual dos recursos*. 9. ed. São Paulo: Revista
dos Tribunais, 2017.

CÂMARA, Alexandre Freitas. *O novo processo civil brasileiro*. 6.
ed. São Paulo: Atlas, 2020.

CHIOVENDA, Giuseppe. *Instituições de direito processual civil*.
Tradução de Paolo Capitanio. 2. ed. Campinas: Bookseller, 2000.

CROSS, Rupert; HARRIS, J. W. *Precedent in English law*. 4. ed.
Oxford: Clarendon Press, 1991.

DIDIER JR., Fredie. *Curso de direito processual civil*. Vol. 1.
20. ed. Salvador: JusPodivm, 2018.

DIDIER JR., Fredie; CUNHA, Leonardo Carneiro da. *Curso de direito
processual civil*. Vol. 3. 16. ed. Salvador: JusPodivm, 2019.

DINAMARCO, Cândido Rangel. *Instituições de direito processual
civil*. 7. ed. São Paulo: Malheiros, 2017. 4 vols.

LIEBMAN, Enrico Tullio. *Eficácia e autoridade da sentença e outros
escritos sobre a coisa julgada*. Tradução de Alfredo Buzaid e
Benvindo Aires. 4. ed. Rio de Janeiro: Forense, 2006.

MACÊDO, Lucas Buril de. *Precedentes judiciais e o direito
processual civil*. 3. ed. Salvador: JusPodivm, 2019.

MARINONI, Luiz Guilherme. *Precedentes obrigatórios*. 5. ed.
São Paulo: Revista dos Tribunais, 2016.

MARINONI, Luiz Guilherme; ARENHART, Sérgio Cruz; MITIDIERO, Daniel.
*Novo código de processo civil comentado*. 3. ed. São Paulo: Revista
dos Tribunais, 2017.

MITIDIERO, Daniel. *Cortes superiores e cortes supremas*. 3. ed.
São Paulo: Revista dos Tribunais, 2017.

NERY JR., Nelson; NERY, Rosa Maria de Andrade. *Código de processo
civil comentado*. 17. ed. São Paulo: Revista dos Tribunais, 2018.

WAMBIER, Teresa Arruda Alvim. *Recurso especial, recurso
extraordinário e ação rescisória*. 3. ed. São Paulo: Revista dos
Tribunais, 2016.

ZANETI JR., Hermes. *O valor vinculante dos precedentes*. 4. ed.
Salvador: JusPodivm, 2019.

---

*Artigo submetido para publicação em [VEÍCULO]. Versão de [DATA].
Paper 1C da série "Raciocínio Jurídico Auditável".*
