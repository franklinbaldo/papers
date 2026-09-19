---
type: "Dogmatic Paper"
title: "Categorias Processuais Civis para Formalização Computacional: mapa descritivo e heurísticas explicitamente delimitadas"
description: "Mapa source-bounded de pedidos, provimentos, escopo recursal e proveniência no CPC 2015, com o quadro de rationes candidatas tratado apenas como heurística computacional para decisões colegiadas fragmentadas."
tags: [paper1c, cpc-2015, formalizacao-juridica, pedidos, provimentos, recursos, ratio-decidendi, proveniencia]
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

# Categorias Processuais Civis para Formalização Computacional: mapa descritivo e heurísticas explicitamente delimitadas

**Franklin Silveira Baldo**  
Independent Researcher

> **Nota de escopo e prioridade.** Este paper separa duas coisas que versões anteriores misturavam. A maior parte do texto é um **mapa descritivo** de categorias e restrições do CPC 2015. Já o `quadro de rationes candidatas` e os estados de anotação de proveniência são **heurísticas propostas para o formalizador**, não regras de direito positivo. A versão arquivável incorpora a auditoria de prontidão e a auditoria temporal específica de 19 de setembro de 2026, corrige os arts. 322/324, 356/355, 485, 487, 503/504 e 1.013 e elimina qualquer inferência automática de coisa julgada, preclusão, aceitação ou efeito devolutivo a partir de mera proveniência textual.

## Resumo

A formalização computacional do processo civil exige que categorias jurídicas distintas não sejam colapsadas em um único tipo de objeto. Este artigo organiza quatro grupos de informação úteis a sistemas de raciocínio jurídico e assistentes de prova: (i) pedidos e suas relações estruturais; (ii) provimentos e os tipos de resolução previstos no CPC; (iii) escopo da cognição recursal; e (iv) proveniência e função argumentativa de afirmações extraídas de documentos processuais.

O texto é deliberadamente conservador. O pedido deve ser **certo** (art. 322) e **determinado** (art. 324), ressalvadas as hipóteses legais de pedido genérico; o julgamento parcial do mérito do art. 356 depende de incontroversibilidade ou das condições de julgamento imediato do art. 355; prescrição e decadência pertencem ao art. 487, II, enquanto as hipóteses homologatórias pertencem ao art. 487, III; razões da decisão não fazem coisa julgada por força do art. 504, e eventual extensão a questão prejudicial depende das condições do art. 503, §1º. O art. 1.013 delimita a matéria impugnada na apelação e distingue-se tanto da cognição de questões relacionadas ao capítulo quanto do julgamento imediato previsto em seu §3º.

Para decisões colegiadas fragmentadas, o artigo não cria uma regra jurídica de extração de `ratio decidendi`. Propõe apenas um **quadro de rationes candidatas**: identificar fundamentos e coalizões de votos, registrar candidatos com suporte, escopo e incerteza e, quando não houver fundamento comum majoritário demonstrável, manter o status `pendente` em vez de fabricar uma ratio vinculante. A mesma disciplina vale para proveniência: derivação textual é metadado; seus efeitos jurídicos devem ser avaliados separadamente segundo as normas aplicáveis.

**Palavras-chave:** formalização jurídica; CPC 2015; pedido; provimento; apelação; ratio decidendi; decisões fragmentadas; proveniência; argumentação jurídica; coisa julgada.

## Abstract

Computational formalization of civil procedure requires legally distinct categories to remain distinct in the data model. This paper organizes four groups of information useful to legal-reasoning systems and proof assistants: (i) claims for relief and their structural relations; (ii) judicial dispositions and statutory types of resolution; (iii) the scope of appellate cognition; and (iv) provenance and argumentative function of propositions extracted from procedural documents.

The account is intentionally source-bounded. Under the Brazilian Code of Civil Procedure, a claim must be **certain** (art. 322) and **determinate** (art. 324), subject to the statutory exceptions for generic claims; partial merits judgment under art. 356 requires either an uncontested claim/portion or the immediate-judgment conditions of art. 355; prescription and limitation belong to art. 487(II), while homologation cases belong to art. 487(III); reasons do not acquire res judicata under art. 504, and prejudicial issues do so only under the conditions of art. 503 §1. Article 1.013 defines the matter devolved on appeal and must not be conflated with either the depth of review within the challenged chapter or the immediate-judgment cases listed in §3.

For fragmented collegiate decisions, the paper does not purport to create a legal rule for extracting a binding `ratio decidendi`. It proposes only a **candidate-ratio table** for formalizers: identify grounds and supporting coalitions, preserve candidate grounds with scope/support/uncertainty metadata, and keep the result `pending` where no shared majority ground can be established. Provenance is treated similarly: textual derivation is metadata, while legal effects must be determined independently under the applicable procedural rules.

**Keywords:** legal formalization; Brazilian civil procedure; claims; judicial dispositions; appeal; ratio decidendi; plurality decisions; provenance; legal argumentation; res judicata.

---

## 1. Propósito e contrato epistemológico

Um formalizador pode produzir uma estrutura sintaticamente impecável e juridicamente errada. Isso ocorre quando distinções processuais são comprimidas durante a tradução para tipos, predicados ou grafos: pedido subsidiário vira simples segundo pedido; fundamento da sentença vira automaticamente coisa julgada; matéria cognoscível no recurso vira sinônimo de capítulo impugnado; ou voto individual vira razão vinculante do colegiado.

Este paper oferece um mapa mínimo para evitar essas compressões. O compromisso é assimétrico:

- quando o CPC fornece regra positiva clara, a representação deve seguir o texto legal e registrar suas condições;
- quando a doutrina fornece uma distinção útil, ela pode orientar o esquema, mas não deve ser promovida a efeito legal automático;
- quando o próprio paper propõe uma heurística computacional, ela deve aparecer como tal, com `status` e limites explícitos.

Essa última regra é particularmente importante nas seções sobre `ratio decidendi` e proveniência. O objetivo não é substituir interpretação jurídica por classificação mecânica; é preservar informação suficiente para que o intérprete — humano ou automatizado — saiba onde a classificação é segura e onde permanece controvertida.

---

## 2. Pedidos como objetos formais

### 2.1 Certeza, determinação e interpretação

O CPC separa requisitos que versões anteriores deste paper haviam atribuído incorretamente aos artigos.

O **art. 322** estabelece que o pedido deve ser **certo**. Seus parágrafos disciplinam, entre outros pontos, a inclusão de consectários legais e a interpretação do pedido considerando o conjunto da postulação e a boa-fé.

O **art. 324** estabelece que o pedido deve ser **determinado**, admitindo pedido genérico nas hipóteses expressamente previstas em seu §1º.

Para o modelo computacional, a consequência não é que todo pedido tenha um valor perfeitamente fechado desde a petição inicial. A consequência é que o objeto precisa registrar separadamente:

- `certeza`: qual tutela ou efeito é solicitado;
- `determinacao`: qual é a extensão/conteúdo individualizado, ou qual exceção legal autoriza genericidade;
- `causa_de_pedir`: fatos e fundamentos que delimitam a controvérsia;
- `excecao_generica`: quando aplicável, fundamento legal para pedido genérico.

Não se deve criar a regra fictícia `art.324 -> pedido expresso + interpretação restritiva`. Essa formulação não corresponde ao CPC 2015 vigente.

### 2.2 Relações entre pedidos

Para formalização, relações estruturais devem ser representadas separadamente da existência dos pedidos:

- **cumulação**: art. 327, observados seus requisitos; os pedidos coexistem no processo;
- **alternatividade**: art. 325, quando a obrigação puder ser cumprida de mais de um modo;
- **subsidiariedade/eventualidade**: art. 326, em ordem sucessiva de preferência; o pedido posterior é examinado conforme a condição estabelecida pela relação;
- **dependência lógica**: algumas pretensões só fazem sentido após a resolução de questão ou pedido antecedente; essa dependência deve ser modelada sem transformá-la, por si, em categoria legal autônoma não prevista no Código.

O ponto computacional é a **regra de ativação**. Um sistema não deve presumir que todos os pedidos presentes em um processo devem ser decididos sob a mesma condição.

### 2.3 Congruência

Os arts. 141 e 492 delimitam a atividade jurisdicional em relação ao objeto submetido. Para fins formais, é útil registrar um vínculo entre cada capítulo do provimento e o pedido/questão processualmente correspondente.

Isso, porém, não autoriza uma inferência puramente textual `novo fundamento -> ultra petita`. Alterações de fundamentação, matérias cognoscíveis de ofício e qualificação jurídica dos fatos exigem análise própria. O modelo deve distinguir **objeto decidido** de **razões usadas para decidir**.

---

## 3. Provimentos e resolução do mérito

### 3.1 Art. 485: sem resolução do mérito

O art. 485 lista hipóteses em que o juiz não resolve o mérito. Duas distinções precisam permanecer literais no esquema:

- **inciso II**: processo parado por mais de um ano por negligência das partes;
- **inciso III**: abandono da causa pelo autor por mais de trinta dias por não promover atos e diligências que lhe incumbiam.

A versão anterior os misturava. Para um formalizador, cada inciso deve ser um valor distinto, acompanhado das condições legais pertinentes e, quando necessário, dos parágrafos que disciplinam intimação e requerimento do réu.

### 3.2 Art. 487: com resolução do mérito

O art. 487 também deve ser representado sem compressões:

- **inciso I**: acolhimento ou rejeição do pedido formulado na ação ou reconvenção;
- **inciso II**: decisão sobre decadência ou prescrição;
- **inciso III**: homologação do reconhecimento da procedência do pedido, da transação ou da renúncia à pretensão formulada.

Portanto, não é correto chamar os incisos II e III conjuntamente de “modalidades homologatórias”.

### 3.3 Julgamento parcial do mérito

O art. 356 permite decisão parcial do mérito quando um ou mais pedidos, ou parcela deles:

1. mostrarem-se incontroversos; ou
2. estiverem em condições de imediato julgamento **nos termos do art. 355**.

A revelia não constitui terceiro gatilho autônomo do art. 356. Ela pode integrar a análise porque o art. 355, II, disciplina uma hipótese de julgamento antecipado quando presentes, cumulativamente, os elementos ali previstos.

Para o esquema:

```text
PartialMeritsTrigger = Uncontroverted | ImmediateJudgmentUnderArt355
```

Não:

```text
PartialMeritsTrigger = Uncontroverted | ImmediateJudgment | Default
```

### 3.4 Coisa julgada não é “status do fundamento”

O art. 503 estabelece que a decisão que julga total ou parcialmente o mérito tem força de lei nos limites da **questão principal expressamente decidida**. Seu §1º estende a disciplina à questão prejudicial apenas se presentes as condições legais: dependência para o julgamento do mérito, contraditório prévio e efetivo e competência do juízo, além do limite do §2º.

O art. 504 exclui da coisa julgada:

- os motivos, ainda que importantes para determinar o alcance da parte dispositiva;
- a verdade dos fatos estabelecida como fundamento da sentença.

Logo, um atributo computacional `fundamento_necessario=true` **não** implica `res_judicata=true`. São dimensões diferentes.

---

## 4. Recurso e escopo de cognição

### 4.1 O objeto recursal deve ser separado do objeto original

Um modelo útil preserva pelo menos três camadas:

1. `pedido_original`;
2. `capitulo_decidido`;
3. `impugnacao_recursal`.

Misturar essas camadas torna impossível verificar congruência recursal, extensão da reforma e preservação de capítulos não impugnados.

### 4.2 Art. 1.013: extensão e questões relacionadas ao capítulo

O caput do art. 1.013 é o ponto de partida: **a apelação devolve ao tribunal o conhecimento da matéria impugnada**.

O §1º amplia a cognição dentro do capítulo devolvido para as questões suscitadas e discutidas no processo, ainda que não solucionadas, desde que relativas ao capítulo impugnado. O §2º trata da pluralidade de fundamentos do pedido ou da defesa.

Isso recomenda uma representação em duas dimensões:

- `extent`: capítulos/matérias impugnados;
- `depth`: questões e fundamentos cognoscíveis para resolver esses capítulos.

A proibição de `reformatio in pejus` é limite distinto e não deve ser usada como sinônimo de extensão. Matérias cognoscíveis de ofício também dependem de fundamento jurídico próprio e não devem ser deduzidas automaticamente do §3º.

### 4.3 Art. 1.013, §3º: julgamento imediato

O §3º disciplina hipóteses em que, estando o processo em condições de imediato julgamento, o tribunal deve decidir desde logo o mérito, incluindo os casos enumerados pelo dispositivo. Ele não é uma cláusula geral de “efeito translativo” nem a fonte universal das matérias de ordem pública.

No modelo, portanto:

```text
AppealScope != ExOfficioIssues != ImmediateMeritsJudgmentUnder1013_3
```

Esses conjuntos podem interagir, mas não são o mesmo objeto.

---

## 5. Ratio decidendi e decisões colegiadas fragmentadas

### 5.1 Resultado majoritário não garante fundamento majoritário

Um colegiado pode formar maioria para o resultado sem formar maioria para uma mesma razão jurídica. A doutrina brasileira de precedentes já identifica esse problema, e a experiência comparada com `plurality opinions` mostra que qualquer método de extração de holding em decisões fragmentadas é sensível à relação lógica entre os fundamentos.

A formalização deve, por isso, registrar separadamente:

- voto;
- resultado apoiado pelo voto;
- fundamentos tratados pelo voto como determinantes;
- relação de compartilhamento ou inclusão entre fundamentos de votos diferentes.

### 5.2 Regra conservadora para fundamento compartilhado

Se uma razão jurídica materialmente equivalente é efetivamente compartilhada pelo número de julgadores necessário para formar a maioria relevante, o sistema pode registrá-la como `shared_majority_ground`, sempre preservando os votos que dão suporte ao rótulo.

Essa classificação é uma conclusão interpretativa auditável; não decorre da ementa nem do resultado numérico isolado.

### 5.3 Quadro de rationes candidatas — **heurística proposta**

A partir de julho de 2026, este paper introduziu um `quadro de rationes candidatas` para casos em que os votos que sustentam o resultado divergem nos fundamentos. A auditoria temporal posterior mostrou que os componentes do problema são antigos: a doutrina brasileira já discute maioria sem fundamento majoritário; `Marks v. United States` (1977) é antecedente comparativo de tentativa de extrair holding de decisão fragmentada; e a própria literatura norte-americana documenta casos em que nenhum “narrowest ground” produz denominador comum coerente.

Assim, o quadro não é apresentado como nova regra jurídica. É uma **heurística de representação**:

```yaml
candidate_ratio:
  proposition: <fundamento identificado>
  supporting_votes: [<votos>]
  scope: <fatos/questões que delimitam o fundamento>
  epistemic_status: candidate | shared-majority | pending
  binding_status: unresolved
```

Procedimento:

1. identificar, voto a voto, os fundamentos materialmente necessários segundo leitura interpretativa;
2. agrupar fundamentos equivalentes ou logicamente compatíveis sem apagar diferenças relevantes;
3. verificar se algum fundamento tem apoio majoritário demonstrável;
4. se houver, registrar a coalizão e a análise que sustenta `shared-majority`;
5. se não houver, preservar **múltiplos candidatos** e marcar `binding_status: unresolved`;
6. se nem a função de um fundamento dentro de um voto puder ser estabelecida com segurança, usar `pending`.

A heurística **não** autoriza escolher como vinculante a ratio candidata “mais próxima” do caso posterior. Similaridade pode ser útil para pesquisa e comparação, mas não substitui a determinação jurídica de autoridade do precedente.

A auditoria específica desta proposta está em `audits/prior-art/paper1c-rationes-candidatas-provenance-2026-09-19.md`.

---

## 6. Proveniência como metadado, não como efeito jurídico

### 6.1 Separar fonte, derivação e função

Para cada afirmação usada na formalização, é útil guardar:

- `source_document`: documento de origem identificado;
- `source_location`: trecho/página/parágrafo quando disponível;
- `derivation`: direta, inferida, transformada ou desconhecida;
- `argument_role`: load-bearing, supporting, alternative, contextual ou pending;
- `confidence`: nível/justificativa da classificação;
- `review_status`: verificado, contestado ou pendente.

Esse perfil é compatível com uma tradição muito anterior de representação de proveniência — inclusive W3C PROV — e com trabalhos de argumentação e ontologias jurídicas. O paper não reivindica novidade para a ideia geral de provenance-aware representation.

### 6.2 `Necessária`, `contingente` e `pendente` são estados de anotação

Versões anteriores usavam `necessária` e `contingente` como se esses rótulos produzissem diretamente consequências processuais. Nesta versão, os termos têm função exclusivamente analítica:

- `necessaria/load-bearing`: segundo a interpretação registrada, remover a proposição mudaria a cadeia justificativa do documento de origem;
- `contingente/supporting`: a proposição está presente, mas a classificação atual não a trata como indispensável à conclusão daquele documento;
- `pendente`: a função não pode ser estabelecida de modo confiável.

Esses rótulos **não** significam automaticamente:

- ratio ou obiter;
- matéria preclusa;
- fato admitido;
- questão coberta por coisa julgada;
- matéria dentro ou fora do efeito devolutivo.

Cada uma dessas consequências tem condições jurídicas próprias.

### 6.3 Derivação entre documentos

É perfeitamente possível representar que uma afirmação de um documento posterior deriva de um documento anterior:

```text
claim_B --derived_from--> claim_A
```

Se o acórdão adota expressamente uma afirmação da sentença, essa adoção é dado relevante para o grafo. Mas a aresta de proveniência não responde, sozinha, se a afirmação integra a ratio, se foi submetida a contraditório, se respeita a congruência, se está dentro do capítulo devolvido ou se produz coisa julgada.

A arquitetura correta é em duas etapas:

1. **traceabilidade**: descobrir de onde a afirmação veio e como foi usada;
2. **efeito jurídico**: aplicar separadamente as regras pertinentes.

---

## 7. Propagação sem inferências automáticas

A expressão “propagação” pode ser mantida como descrição de um fenômeno textual: proposição A aparece em documento 1 e é citada, adotada ou transformada em documento 2. O que não se pode fazer é atribuir automaticamente efeito processual ao percurso.

Em especial:

- ausência de embargos de declaração contra uma afirmação **não** equivale, por si só, a aceitação jurídica daquela afirmação;
- a falta de impugnação de um fundamento precisa ser analisada à luz do objeto recursal, das regras de preclusão e do tipo de questão; não existe regra geral `silêncio -> fundamento aceito`;
- fundamento de sentença ou acórdão não transita em julgado só porque foi importante à decisão: art. 504 exclui os motivos; questão prejudicial exige art. 503, §1º;
- incorporação ativa de fundamento anterior não é automaticamente `ultra petita`; é preciso verificar objeto, causa de pedir, contraditório, qualificação jurídica, escopo recursal e demais normas aplicáveis.

O sistema de formalização deve, portanto, sinalizar possíveis mudanças de papel de uma afirmação entre documentos, mas deixar a classificação do efeito jurídico para regras independentes e auditáveis.

---

## 8. Esquema computacional mínimo

Um esquema de implementação pode começar com objetos explícitos e poucos defaults:

```yaml
procedural_claim:
  id: <stable-id>
  requested_relief: <text/ref>
  certainty: <declared>
  determinacy: <declared | generic-with-statutory-basis>
  relation_to_other_claims: [cumulative | alternative | subsidiary | dependent]

disposition:
  target_claim: <id>
  cpc_basis: <485.x | 487.x | 356 | other>
  resolves_merits: <true|false>

appeal:
  challenged_chapters: [<refs>]
  related_questions: [<refs>]
  immediate_judgment_basis: <1013.3.x | null>

statement:
  source_document: <ref>
  source_location: <ref>
  derivation: <direct | inferred | transformed | unknown>
  argument_role: <load-bearing | supporting | alternative | contextual | pending>
  confidence: <declared>

candidate_ratio:
  proposition: <statement-ref>
  supporting_votes: [<refs>]
  scope: <declared>
  epistemic_status: <candidate | shared-majority | pending>
  binding_status: <resolved-by-legal-analysis | unresolved>
```

A vantagem de um esquema assim é que ele recusa defaults perigosos. `binding_status`, `res_judicata`, `preclusion` e `admitted` não são inferidos simplesmente da posição de uma frase no documento.

---

## 9. Limitações

Primeiro, a tradução de categorias jurídicas para tipos computacionais não elimina interpretação. Termos como “fundamento necessário”, “capítulo impugnado”, “questão prejudicial” ou “mesmo fundamento” exigem leitura jurídica.

Segundo, a classificação de votos fragmentados é especialmente resistente à automação. Similaridade semântica entre textos não basta para afirmar identidade normativa de fundamentos.

Terceiro, o `quadro de rationes candidatas` é uma proposta operacional, não uma regra de precedentes brasileiros. Seu resultado deve permanecer contestável e auditável.

Quarto, o mapa legislativo deste paper não substitui análise de jurisprudência, legislação superveniente ou regime especial aplicável a um processo concreto. A lei citada deve ser verificada na versão vigente ao tempo da aplicação.

Quinto, a proveniência registra o caminho informacional de uma afirmação, mas não sua verdade nem sua força normativa.

---

## 10. Conclusão

A contribuição útil deste paper é a separação disciplinada de camadas.

O CPC fornece categorias jurídicas: certeza e determinação do pedido, hipóteses de resolução, condições para julgamento parcial, limites da coisa julgada e estrutura da cognição recursal. Essas categorias devem ser representadas de modo fiel ao texto e sem atalhos.

A teoria de precedentes fornece um problema adicional: resultado colegiado e fundamento majoritário não são sinônimos. O `quadro de rationes candidatas` pode ajudar o formalizador a não perder os fundamentos concorrentes, desde que a ausência de maioria argumentativa produza **incerteza explícita**, não uma ratio artificial.

Por fim, proveniência é essencial para auditabilidade, mas não substitui direito processual. Saber de onde uma proposição veio é pré-condição para avaliar seu papel; não é prova de coisa julgada, preclusão, admissão ou vinculação.

Uma formalização juridicamente segura começa, portanto, por não confundir o que o sistema **observa**, o que o intérprete **classifica** e o que o direito **faz decorrer** dessa classificação.

---

## Referências

ASSIS, Araken de. *Manual dos recursos*. 9. ed. São Paulo: Revista dos Tribunais, 2017.

BRASIL. Lei nº 13.105, de 16 de março de 2015. Código de Processo Civil, texto compilado. <https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm>.

CASANOVAS, Pompeu et al. An OWL ontology library representing judicial interpretations. *Semantic Web*, 2014/2016. DOI: 10.3233/SW-140146.

CROSS, Rupert; HARRIS, J. W. *Precedent in English Law*. 4. ed. Oxford: Clarendon Press, 1991.

LEBO, Timothy; SAHOO, Satya; MCGUINNESS, Deborah (eds.). *PROV-O: The PROV Ontology*. W3C Recommendation, 30 Apr. 2013. <https://www.w3.org/TR/2013/REC-prov-o-20130430/>.

MACÊDO, Lucas Buril de. *Precedentes judiciais e o direito processual civil*. 3. ed. Salvador: JusPodivm, 2019.

MARINONI, Luiz Guilherme. *Precedentes obrigatórios*. 5. ed. São Paulo: Revista dos Tribunais, 2016.

MARINONI, Luiz Guilherme. Julgamento nas cortes supremas: precedentes e decisão do recurso diante do novo CPC. São Paulo: Revista dos Tribunais, 2017.

MARKS v. UNITED STATES, 430 U.S. 188 (1977). <https://supreme.justia.com/cases/federal/us/430/188/>.

MITIDIERO, Daniel. *Cortes superiores e cortes supremas*. 3. ed. São Paulo: Revista dos Tribunais, 2017.

WAMBIER, Teresa Arruda Alvim. *Recurso especial, recurso extraordinário e ação rescisória*. 3. ed. São Paulo: Revista dos Tribunais, 2016.

---

*Paper 1C da série "Raciocínio Jurídico Auditável". Versão 0.1 preparada para arquivamento reproduzível no Zenodo.*