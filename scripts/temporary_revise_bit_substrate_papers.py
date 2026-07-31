from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path.cwd()


def run(*args: str) -> None:
    subprocess.run(args, cwd=REPO, check=True)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}: {old[:120]!r}")
    return text.replace(old, new, 1)


def revise_branch(
    branch: str,
    path_name: str,
    replacements: list[tuple[str, str]],
    message: str,
    remove_paths: tuple[str, ...] = (),
) -> None:
    run("git", "fetch", "origin", branch)
    run("git", "checkout", "-B", branch, f"origin/{branch}")

    path = REPO / path_name
    text = path.read_text()
    for index, (old, new) in enumerate(replacements, start=1):
        text = replace_once(text, old, new, f"{branch}:{path_name}:replacement-{index}")
    path.write_text(text)

    for remove_path in remove_paths:
        target = REPO / remove_path
        if target.exists():
            target.unlink()

    run("git", "add", "-A")
    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=REPO, check=False
    )
    if status.returncode == 0:
        print(f"{branch}: no changes")
        return
    run("git", "commit", "-m", message)
    run("git", "push", "origin", f"HEAD:refs/heads/{branch}")


def main() -> None:
    run("git", "config", "user.name", "github-actions[bot]")
    run(
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )

    revise_branch(
        "paper/generative-machine-teaching",
        "generative_machine_teaching.md",
        [
            (
                r"""This paper proposes **generative machine teaching**, a paradigm in which lessons are deterministic programs whose outputs are the only pedagogical evidence available to a student. It then introduces a stronger foundational substrate: a **self-tokenizing concatenative language**. The physical channel contains only two primitive marks, and concatenation is the only primitive operation. A derived object becomes a token when a procedural demonstration constructs it from previously available objects, verifies its expansion, assigns it a stable registry identifier, and makes that identifier available for reuse in later turns.""",
                r"""This paper proposes **generative machine teaching**, a paradigm in which lessons are deterministic programs whose outputs are the only pedagogical evidence available to a student. It then introduces a stronger foundational substrate: a **self-tokenizing concatenative language**. The physical channel contains only two primitive marks, and concatenation is the only primitive operation. In the strongest benchmark, the learner's externally scored predictive task remains next-bit prediction on the continuous binary stream. A derived object becomes a token when a procedural demonstration constructs it from previously available objects, verifies its expansion, assigns it a stable registry identifier, and makes that identifier available for reuse in later inference. Tokens are therefore endogenous, context-dependent instruments for prediction and competence, not prediction targets supplied in advance.""",
            ),
            (
                r"""The strongest benchmark presents only a continuous binary stream. The student must infer turn boundaries, discover concatenation, recover the registry protocol, identify reusable substrings as symbols, predict newly constructed token identifiers, reconstruct or improve assembly proofs, recognize the teacher as a structured action-generating agent, and acquire executable algorithms expressed through the emerging vocabulary. The central empirical question becomes: **what is the shortest sequence of procedural demonstrations from which a given learner can construct a useful tokenizer and acquire a given algorithm?**""",
                r"""The strongest benchmark presents only a continuous binary stream and evaluates the learner through the primitive distribution $p(b_{t+1}\mid b_{1:t})$. The student may infer turn boundaries, discover concatenation, recover a registry protocol, identify reusable substrings as symbols, reconstruct or improve assembly proofs, recognize the teacher as a structured action-generating agent, and acquire executable algorithms expressed through an emerging vocabulary. Registry-ID prediction and proof recovery are secondary diagnostics of the learned representation, not replacements for the bit-level task. The central empirical question becomes: **what is the shortest sequence of procedural demonstrations from which a given learner can improve primitive prediction, construct a useful adaptive symbolic system, and acquire a given algorithm?**""",
            ),
            (
                r"""This paper studies a more austere problem. A learner receives a channel containing only two physical marks. It may receive no natural-language instructions, no permanent token boundaries, no lesson boundaries, and no fixed semantic vocabulary. Instead of assuming tokens, the curriculum must teach the learner how reusable symbolic units come into existence.""",
                r"""This paper studies a more austere problem. A learner receives a channel containing only two physical marks. It may receive no natural-language instructions, no permanent token boundaries, no lesson boundaries, and no fixed semantic vocabulary. Its primitive observable task is to predict the next mark from the marks already observed. Instead of assuming tokens, the curriculum permits the learner to construct reusable symbolic units whenever doing so improves prediction, execution, transfer, or total cost in the current context.""",
            ),
            (
                r"""$$
E := 0 \Vert 1 = 01.
$$

The token named *begin* can then be demonstrated as:""",
                r"""$$
E := 0 \Vert 1 = 01.
$$

Here `E` is a physically non-empty codeword assigned the protocol-level role *empty*. It is neither the empty string nor the set-theoretic empty set; its role is learned from its procedural use.

The token named *begin* can then be demonstrated as:""",
            ),
            (
                r"""This changes the role of tokenization. A substring is not a token merely because an external preprocessing algorithm selected it. It becomes a token when the language demonstrates its construction, records a stable identity and proof, and begins using that identity compositionally. The language therefore incorporates its own tokenizer. Its vocabulary grows through the same procedural turns by which it teaches operations and algorithms.""",
                r"""This changes the role of tokenization. A substring is not a token merely because an external preprocessing algorithm selected it, nor because the benchmark declares one segmentation correct. It becomes a token when the learner or shared protocol gives it stable, reusable symbolic function grounded in an expandable construction. The language therefore incorporates an adaptive tokenizer whose vocabulary can change with the learner, target, history, and current predictive context. The same bits may be grouped in one context and left decomposed in another. Vocabulary growth occurs through the same procedural turns by which operations and algorithms are learned.""",
            ),
            (
                r"""A standard large language model still has a fixed *physical* tokenizer and output head. The proposal does not erase that engineering fact. It introduces an additional **endogenous symbolic layer**: a registered token identifier can be represented by a sequence of physical model tokens while functioning as one learned symbol in the protocol. A stronger architectural track may dynamically allocate embeddings and output slots for newly registered symbols. The benchmark must distinguish these two meanings of “new token.”""",
                r"""A standard large language model still has a fixed host tokenizer and output head. The proposal does not erase that engineering fact. In the strict benchmark, host tokens ultimately encode a stream of primitive bits, and the common external score is computed at that bit interface. The proposal introduces an additional **endogenous symbolic layer**: a registered token identifier can be represented by a sequence of host tokens while functioning as one learned symbol in the protocol. A stronger architectural track may dynamically allocate embeddings and internal prediction slots for newly registered symbols. The benchmark must distinguish host tokens, primitive bits, and endogenous symbols, and must not mistake agreement on internal symbols for the primary learning objective.""",
            ),
            (
                r"""The proposed registry differs in four respects. First, token creation is an explicit procedural event rather than only a statistical merge. Second, every symbol carries a reproducible construction proof. Third, tokens persist as addressable objects available to later lessons. Fourth, token selection can be optimized for teaching an algorithm, not only corpus compression or end-task loss.""",
                r"""The proposed registry differs in five respects. First, token creation is an explicit procedural event rather than only a statistical merge. Second, every symbol carries a reproducible construction proof. Third, tokens persist as addressable objects available to later lessons. Fourth, token selection can be optimized for teaching an algorithm, not only corpus compression or end-task loss. Fifth, tokenization is learner-, target-, history-, and context-relative while the primitive prediction interface remains fixed, so alternative registries may be functionally equivalent without sharing literal boundaries or identifiers.""",
            ),
            (
                r"""This is the central self-tokenizing mechanism. Tokenization is not a preprocessing step performed before the language exists. It is an internal state transition of the language.""",
                r"""This is the central self-tokenizing mechanism. Tokenization is not a preprocessing step performed before the language exists. It is an internal state transition of the language and learner. The physical evidence remains the bit stream, and the learner may continue to be evaluated by next-bit loss while using the registry as an internal computational scale. No unique registry is presumed: two registries are functionally equivalent when, after charging their costs, they support comparable primitive prediction, algorithm execution, and transfer.""",
            ),
            (
                r"""The optimal tokenization is therefore potentially learner-relative and target-relative. A useful token is not merely frequent; it is a reusable assembly that improves future teaching or execution.""",
                r"""The optimal tokenization is therefore learner-, target-, history-, and context-relative. A useful token is not merely frequent; it is a reusable assembly that improves future prediction, teaching, execution, or transfer after its cost is charged. The token may cease to be useful when the context changes, and a different decomposition may realize the same competence.""",
            ),
            (
                r"""Claims about “predicting a new token” must identify which level is meant.""",
                r"""Claims about “predicting a new token” must identify which level is meant and must remain secondary to the primitive observable task. A learner can exploit endogenous tokens while emitting only next-bit probabilities, and two learners can succeed with different internal token hierarchies.""",
            ),
            (
                r"""This is stronger than ordering a fixed dataset. The search decides which experiences to generate, which constructions to register as symbols, when to introduce them, and how to reuse them later.""",
                r"""This is stronger than ordering a fixed dataset. The search decides which experiences to generate, which constructions to register as symbols, when to introduce them, and how to reuse them later. The registry is optimized as an internal instrument under a common primitive prediction and competence interface; exact recovery of the teacher's registry is not required when another registry achieves equivalent observable behavior at comparable total cost.""",
            ),
            (
                r"""A separate tokenizer-emergence threshold is:

$$
T_{q,r}(M,\mathcal C)
=
\min\{n:\Pr[\operatorname{TokScore}(n)\geq q]\geq r\}.
$$""",
                r"""A separate representation-emergence threshold may be defined as:

$$
T^{\mathrm{rep}}_{q,r}(M,\mathcal C)
=
\min\{n:\Pr[\operatorname{RepScore}(n)\geq q]\geq r\}.
$$

Here $\operatorname{RepScore}$ must combine functional quantities such as next-bit gain, task competence, transfer, expansion correctness, and total registry cost. It must not reduce to literal boundary or identifier agreement with one designated tokenizer.""",
            ),
            (
                r"""The learner must:

- identify the two elementary marks;""",
                r"""The learner must:

- predict the next primitive bit under a common bit-level scoring rule;
- identify the two elementary marks;""",
            ),
            (
                r"""### 9.1 Raw prediction is insufficient

High next-bit accuracy can arise without recovering symbols, procedures, agents, or algorithms. Evaluation must separate physical prediction from endogenous symbolic competence.""",
                r"""### 9.1 Next-bit prediction is primitive but not exhaustive

Next-bit prediction is the common externally observable task in the strongest track. High next-bit accuracy alone, however, does not establish that the learner acquired reusable procedures, an executable algorithm, or a transferable representation. Evaluation therefore begins with physical prediction and supplements it with functional diagnostics of symbolic competence; it does not replace the primitive task with token matching.""",
            ),
            (
                r"""### 9.2 Registry recovery

Measure exact or functional recovery of:""",
                r"""### 9.2 Registry recovery as a diagnostic

Where an explicit registry is part of the experimental protocol, measure exact or functional recovery of:""",
            ),
            (
                r"""The teacher's registry is not necessarily the only valid tokenization. Functional equivalence and downstream utility must accompany exact-match scores.""",
                r"""The teacher's registry is not necessarily the only valid tokenization. Exact-match scores are secondary. Functional equivalence should be established through primitive predictive loss, executable behavior, transfer, perturbation stability, expansion correctness where required, and total representational cost.""",
            ),
            (
                r"""### H4: Optimal tokenization is learner-relative

Registry rankings will differ across transformers, recurrent models, symbolic learners, and pretrained LLMs.""",
                r"""### H4: Optimal tokenization is learner- and context-relative

Registry rankings will differ across transformers, recurrent models, symbolic learners, pretrained LLMs, target tasks, and interaction histories. Distinct registries may nevertheless be functionally equivalent at the primitive prediction and task interfaces.""",
            ),
            (
                r"""### H8: Virtual and native self-tokenization differ

Architectures with native dynamic vocabulary support will outperform fixed-vocabulary models on registry-ID prediction after controlling for physical input length.""",
                r"""### H8: Virtual and native self-tokenization differ

Architectures with native dynamic vocabulary support may achieve lower primitive next-bit loss, lower computational cost, or faster task acquisition than fixed-vocabulary models after controlling for physical input length and total registry cost. Registry-ID prediction is reported only as a secondary mechanism diagnostic.""",
            ),
            (
                r"""Present reusable constructions and symmetry-related variants. Compare single-bit, BPE, SentencePiece, frequency-only, compression-only, symmetry-aware, and proof-indexed registries. Test recursive registration by allowing sequences of learned IDs to become higher-order symbols, and report the total cost of the registry plus indexed transcript rather than compression of the transcript alone.""",
                r"""Present reusable constructions and symmetry-related variants. Compare single-bit, BPE, SentencePiece, frequency-only, compression-only, symmetry-aware, and proof-indexed registries under the same next-bit prediction interface. Test recursive registration by allowing sequences of learned IDs to become higher-order symbols, and report primitive predictive loss, task competence, functional equivalence among alternative registries, and the total cost of the registry plus indexed transcript rather than compression of the transcript alone.""",
            ),
            (
                r"""### 14.9 What should count as a symbol?

Frequency, compression, proof minimality, pedagogical information, and downstream utility may favor different registries. The benchmark should report Pareto frontiers rather than assume one scalar objective is universally correct.""",
                r"""### 14.9 What should count as a symbol?

Frequency, compression, proof minimality, pedagogical information, primitive predictive gain, and downstream utility may favor different registries in different contexts. The benchmark should report Pareto frontiers and equivalence classes of functionally adequate registries rather than assume one scalar objective or one literal segmentation is universally correct.""",
            ),
            (
                r"""### 15.2 Next-token prediction at two levels

An LLM predicts physical tokens. In the proposed protocol it may simultaneously learn to predict *endogenous* tokens—registry IDs whose expansions are themselves strings of physical tokens. This layered view converts next-token prediction into a mechanism for constructing a new symbolic alphabet without pretending that the underlying model vocabulary has already changed.""",
                r"""### 15.2 Next-bit prediction as substrate, tokenization as instrument

The strict learner predicts the next primitive bit. A host LLM may implement that distribution through its fixed physical tokens while simultaneously learning *endogenous* symbols—registry IDs whose expansions ultimately resolve to bit strings. This layered view makes tokenization an adaptive internal mechanism for constructing useful symbolic scales without changing the external evidence or pretending that one internal alphabet is the learning target.""",
            ),
            (
                r"""This paper proposed a framework in which deterministic lessons teach not only algorithms but the symbolic vocabulary required to express them. The physical substrate contains two marks, and concatenation is the only primitive operation. A procedural demonstration joins previously available objects, verifies the result, registers it under a stable identifier, and makes it available as one symbol in later turns.""",
                r"""This paper proposed a framework in which deterministic lessons teach not only algorithms but adaptive symbolic vocabularies that can make prediction and execution more efficient. The physical substrate contains two marks, concatenation is the only primitive operation, and the externally scored primitive task is next-bit prediction. A procedural demonstration joins previously available objects, verifies the result, registers it under a stable identifier, and makes it available as one possible internal symbol in later turns.""",
            ),
            (
                r"""The resulting registry is self-tokenizing. It stores expansions, alternative construction proofs, Gödel-style proof codes, assembly metadata, and stable identities. Tokenization therefore emerges from interaction rather than being imposed before learning. A model with a fixed physical vocabulary can participate through virtual symbolic IDs, while stronger architectures can implement native dynamic tokens.""",
                r"""The resulting registry is self-tokenizing. It stores expansions, alternative construction proofs, Gödel-style proof codes, assembly metadata, and stable identities. Tokenization therefore emerges from interaction rather than being imposed before learning, and remains revisable, context-dependent, and non-unique. A model with a fixed host vocabulary can participate through virtual symbolic IDs, while stronger architectures can implement native dynamic tokens; both remain comparable at the primitive bit and task interfaces.""",
            ),
            (
                r"""> What is the shortest sequence of procedural demonstrations from which a given learner can recognize its teacher, construct a useful tokenizer, and acquire a given executable algorithm?""",
                r"""> What is the shortest sequence of procedural demonstrations from which a given learner can recognize its teacher, improve prediction of the primitive stream, construct any functionally useful context-adaptive symbolic system, and acquire a given executable algorithm?""",
            ),
        ],
        "paper: make next-bit prediction the primitive learning interface",
        remove_paths=(".github/workflows/temporary-stacked-paper-revisions.yml",),
    )

    revise_branch(
        "paper/informational-time",
        "informational_time.md",
        [
            (
                r"""The framework distinguishes causal time from representational time. A long causal history may be replaced by a short symbolic index without erasing the events that occurred, provided the index retains an executable expansion proof. This motivates **recursive endogenous tokenization**: sequences of primitive marks become tokens; sequences of token indices become higher-order tokens; and the process continues until no admissible registration reduces the combined cost of the registry and the indexed transcript. The endpoint is a registry-relative irreducible residue, not an absolute computable incompressible core.""",
                r"""The framework distinguishes causal time from representational time. A long causal history may be replaced by a short symbolic index without erasing the events that occurred, provided the index retains an executable expansion proof. This motivates **recursive endogenous tokenization**: sequences of primitive marks become tokens; sequences of token indices become higher-order tokens; and the process continues until no admissible registration reduces the combined cost of the registry and the indexed transcript. These tokens are observer-relative, context-adaptive instruments. They do not replace the primitive physical stream or become mandatory external prediction targets. The endpoint is a registry-relative irreducible residue, not an absolute computable incompressible core.""",
            ),
            (
                r"""The motivating companion framework, developed in `generative_machine_teaching.md`, introduces a self-tokenizing language in which concatenation is the only primitive operation. A demonstrated construction receives a stable index and an executable proof, allowing later procedures to use the construction as one symbol. The present paper asks what follows when that mechanism is applied recursively to causal histories themselves.""",
                r"""The motivating companion framework, developed in `generative_machine_teaching.md`, introduces a self-tokenizing language in which concatenation is the only primitive operation. In its strict track, the learner remains externally evaluated on the primitive bit stream, while a demonstrated construction may receive a stable index and executable proof so that later inference can use it as one internal symbol. The present paper asks what follows when that adaptive representational mechanism is applied recursively to causal histories themselves.""",
            ),
            (
                r"""- that a short token makes the causal history it denotes cease to have occurred.""",
                r"""- that a short token makes the causal history it denotes cease to have occurred;
- that one registry, segmentation, or token hierarchy is uniquely correct independently of observer, context, and predictive task.""",
            ),
            (
                r"""Begin with a physical alphabet:

$$
\Sigma_0=\{0,1\}.
$$

After registering useful strings over $\Sigma_0$, obtain a symbolic alphabet $\Sigma_1$.""",
                r"""Begin with a physical alphabet:

$$
\Sigma_0=\{0,1\}.
$$

The primitive observable interface remains at this level. In a binary prediction benchmark, the learner may be scored throughout on $p(b_{t+1}\mid b_{1:t})$ even while it constructs higher symbolic levels internally. After registering useful strings over $\Sigma_0$, obtain a symbolic alphabet $\Sigma_1$.""",
            ),
            (
                r"""A token may be worthwhile even when it does not compress the past if it substantially reduces expected future teaching, prediction, or action cost.""",
                r"""A token may be worthwhile even when it does not compress the past if it substantially reduces expected future teaching, primitive prediction, or action cost. Its legitimacy is functional and context-dependent: another registry may be equally good if it yields comparable observable predictions, competence, transfer, and total cost.""",
            ),
            (
                r"""Let $Y$ be the future variable, target action, or task output whose prediction matters. Define predictive semantic yield:""",
                r"""Let $Y$ be the future variable, target action, primitive next observation, or task output whose prediction matters. For a binary stream, $Y$ may simply be $b_{t+1}$. Define predictive semantic yield:""",
            ),
            (
                r"""A shared token is evidence that:

1. a structure recurred or transformed systematically;
2. the demonstrator used it as a unit;
3. the observer identified and registered it;
4. later interaction successfully reused the index.

Tokens therefore mark accumulated predictive coordination, not merely static compression.""",
                r"""A shared token is one possible record that:

1. a structure recurred or transformed systematically;
2. the demonstrator used it as a unit;
3. the observer identified and registered it;
4. later interaction successfully reused the index.

Tokens therefore can mark accumulated predictive coordination, not merely static compression. They are not the only possible record: observers may construct different, functionally equivalent registries, and coordination must ultimately be evaluated at the primitive observation and action interfaces.""",
            ),
            (
                r"""Allow tokens at level $k$ to become atoms for candidate tokens at level $k+1$. Measure:

- total registry cost;
- indexed transcript length;
- proof depth;
- causal history recovery;
- compression fixed points;
- predictive yield;
- transfer to larger unseen structures.""",
                r"""Allow tokens at level $k$ to become atoms for candidate tokens at level $k+1$. Keep the primitive bit or observation prediction interface fixed across conditions. Measure:

- total registry cost;
- indexed transcript length;
- proof depth;
- causal history recovery;
- primitive predictive loss;
- functional equivalence among alternative registries;
- compression fixed points;
- predictive yield;
- transfer to larger unseen structures.""",
            ),
            (
                r"""Proof-preserving tokenization can replace long histories with short indices without erasing the event order that produced them. Because indices can themselves be concatenated and registered, tokenization becomes recursive. The process continues until the combined registry and transcript reach a relative fixed point under the admitted construction language and cost function.""",
                r"""Proof-preserving tokenization can replace long histories with short indices without erasing the event order that produced them. Because indices can themselves be concatenated and registered, tokenization becomes recursive. The physical evidence nevertheless remains the primitive stream; the hierarchy is an adaptive representational strategy whose value is measured by prediction, action, reconstruction, and cost. The process continues until the combined registry and transcript reach a relative fixed point under the admitted construction language and cost function.""",
            ),
            (
                r"""The central empirical question is not whether a long sequence is improbable. It is whether interaction produces a proof-preserving representation that compresses what has occurred, predicts what comes next, and does so after the full cost of the representation itself is paid.""",
                r"""The central empirical question is not whether a long sequence is improbable or whether one canonical tokenization is recovered. It is whether interaction produces a proof-preserving representation that compresses what has occurred, improves prediction at the primitive interface, supports action and transfer, and does so after the full cost of the representation itself is paid.""",
            ),
        ],
        "paper: clarify primitive prediction beneath recursive tokenization",
    )

    revise_branch(
        "paper/informational-time-negentropy",
        "informational_time_negentropy_clarifications.md",
        [
            (
                r"""Observed order may be caused by $A$ itself, by the interaction protocol, or by
an external source. Recognition of another therefore requires comparison among
at least three model families:""",
                r"""Observed order may be caused by $A$ itself, by the interaction protocol, by an
external structured law, or by an agent-like source. Recognition of another
agent therefore requires comparison among at least four model families:""",
            ),
            (
                r"""$$
\mathcal M_{\mathrm{source}}^{A}
\quad
\text{a persistent external source of organized causal distinctions}.
$$

The other becomes recognizable when a source model predicts and compresses the
continuing interaction better than both the maximum-entropy null and the best
self-generated explanation, after the full costs of the source model, registry,
search, and fitted parameters are charged.""",
                r"""$$
\mathcal M_{\mathrm{law}}^{A}
\quad
\text{a persistent external structured process described by non-agent dynamics},
$$

$$
\mathcal M_{\mathrm{agent}}^{A}
\quad
\text{a persistent organized source whose latent state and contingent behavior}
\text{ support an agent-level model}.
$$

An external source becomes recognizable when an external model defeats maximum
entropy and self-generation. Agency requires the stronger result that an agent
model predicts and compresses the continuing interaction better than the best
structured non-agent law as well, after the full costs of the model, registry,
search, and fitted parameters are charged. High predictability, concentration,
or deterministic limiting observables can therefore establish structure without
establishing agency.""",
            ),
            (
                r"""> For observer $A$, an agent is a causal source whose persistent production,
> conservation, and transformation of organized distinctions is better modeled
> as a continuing structured generator than as a maximum-entropy fluctuation or
> as a consequence of $A$ alone.""",
                r"""> For observer $A$, an agent is a causal source whose persistent production,
> conservation, and transformation of organized distinctions is better modeled
> at an agent-relevant causal scale than as a maximum-entropy fluctuation, a
> consequence of $A$ alone, or the best available structured non-agent law.""",
            ),
            (
                r"""Let $D_{1:T}$ be the interaction available to $A$ at time $T$. Define the best
fluctuation-or-self account:

$$
L_{0,T}
=
\min_{M\in
\mathcal M_{\max}^{A}\cup\mathcal M_{\mathrm{self}}^{A}}
L(D_{1:T},M).
$$

Define the best persistent-source account:

$$
L_{1,T}
=
\min_{M\in\mathcal M_{\mathrm{source}}^{A}}
\left[
L(R_T,M)+L(D_{1:T}\mid R_T,M)
\right].
$$""",
                r"""Let $D_{1:T}$ be the interaction available to $A$ at time $T$. Define the best
non-agent account:

$$
L_{0,T}
=
\min_{M\in
\mathcal M_{\max}^{A}
\cup\mathcal M_{\mathrm{self}}^{A}
\cup\mathcal M_{\mathrm{law}}^{A}}
L(D_{1:T},M).
$$

Define the best agent-level account:

$$
L_{1,T}
=
\min_{M\in\mathcal M_{\mathrm{agent}}^{A}}
\left[
L(R_T,M)+L(D_{1:T}\mid R_T,M)
\right].
$$""",
            ),
            (
                r"""Positive evidence means that the persistent-source account compresses the
observed history better after complete accounting. Recognition additionally
requires prospective success: the source model must continue to predict held-out
observations or intervention responses better than the fluctuation and self
models.""",
                r"""Positive evidence means that the agent-level account compresses the observed
history better after complete accounting. Recognition additionally requires
prospective success: the agent model must continue to predict held-out primitive
observations or intervention responses better than the fluctuation, self, and
structured-law models. The registry is an observer-relative instrument in this
comparison; exact recovery of one token hierarchy is neither necessary nor
sufficient for recognizing agency.""",
            ),
            (
                r"""> the accumulated informational time at which a persistent external-source
> model becomes and remains a better predictive and descriptive account of the
> interaction than both observer-relative maximum entropy and self-generated
> order.""",
                r"""> the accumulated informational time at which an agent-level model becomes and
> remains a better predictive and descriptive account of the interaction than
> observer-relative maximum entropy, self-generated order, and the strongest
> admissible structured non-agent law.""",
            ),
            (
                r"""- self-caused structure versus externally responsive structure;
- passive observation versus interventions selected by $A$;""",
                r"""- self-caused structure versus externally responsive structure;
- structured stochastic or deterministic laws with stable macroscopic observables versus agent-like sources;
- passive observation versus interventions selected by $A$;""",
            ),
            (
                r"""A useful benchmark should not ask only whether an agent model defeats random,
stationary, or deterministic baselines. It should ask when a continuing-source
model earns its additional commitments over the strongest fluctuation and
self-generation explanations available to the observer.""",
                r"""A useful benchmark should not ask only whether an agent model defeats random,
stationary, or simplistic deterministic baselines. It should ask when an
agent-level model earns its additional commitments over the strongest
fluctuation, self-generation, and structured external-law explanations available
to the observer. All models should be compared at the same primitive observation
interface even when they use different internal tokenizations.""",
            ),
            (
                r"""### H5: Sufficient scale makes rare finite order unsurprising

For any fixed finite organized pattern with nonzero per-opportunity probability,
the probability of at least one occurrence increases toward one as the number
of approximately independent opportunities grows.""",
                r"""### H5: Sufficient scale makes rare finite order unsurprising

For any fixed finite organized pattern with nonzero per-opportunity probability,
the probability of at least one occurrence increases toward one as the number
of approximately independent opportunities grows.

### H6: Structured predictability does not by itself establish agency

High-dimensional stochastic ensembles, deterministic dynamics, or other
non-agent processes may yield persistent, sharply predictable macroscopic
observables. When a structured-law model explains those observables at lower
total cost, an agent model should not be selected merely because the process is
ordered or predictable.""",
            ),
            (
                r"""What reveals the other is the accumulation of a causal history in which order
persists, produces further order, and answers intervention in ways that cannot
be economically attributed either to fluctuation or to the observer alone.
Recursive tokenization records that history; symmetry identifies the invariants
it preserves; prediction tests whether the inferred source continues to exist as
an explanatory object.""",
                r"""What reveals an external source is the accumulation of a causal history in
which order persists beyond fluctuation and self-generation. What can justify an
agent-level interpretation is the further result that the source's continuing
organization and intervention-sensitive behavior cannot be economically
captured by the best structured non-agent law. Recursive tokenization may record
that history, but it remains an observer-relative representational instrument;
symmetry identifies candidate invariants, and primitive prediction tests whether
the inferred causal scale continues to earn its explanatory role.""",
            ),
            (
                r"""\text{maximum-entropy null}
\rightarrow
\text{local fluctuation}
\rightarrow
\text{persistent causal organization}
\rightarrow
\text{recognition of another source}.""",
                r"""\text{maximum-entropy null}
\rightarrow
\text{local fluctuation}
\rightarrow
\text{persistent structured law}
\rightarrow
\text{agent-level causal organization}
\rightarrow
\text{recognition of another agent}.""",
            ),
            (
                r"""Agency is the relational interpretation earned at the final step. The framework
leaves open which physical, biological, computational, collective, or
evolutionary processes will earn it.""",
                r"""Agency is the relational interpretation earned at the final step, not a synonym
for order, predictability, or compressibility. The framework leaves open which
physical, biological, computational, collective, or evolutionary processes will
earn it and at which causal scale.""",
            ),
        ],
        "paper: distinguish adaptive agency from structured external law",
    )

    revise_branch(
        "paper/pedagogical-signal-extraction",
        "pedagogical_signal_extraction.md",
        [
            (
                r"""The central hypothesis is that optimal teaching does not reduce to maximal compression or maximal raw entropy. An optimal pedagogical message may use highly diverse, locally irregular demonstrations while preserving a stable higher-order grammar that makes those demonstrations progressively decodable. The complementary learner hypothesis is that a good learner is not the system that finds the greatest number of patterns in a finite transcript, but the system that extracts compact invariants that survive new data, perturbation, and intervention while improving prediction of the teacher and execution of the target function.""",
                r"""The central hypothesis is that optimal teaching does not reduce to maximal compression or maximal raw entropy. An optimal pedagogical message may use highly diverse, locally irregular demonstrations while preserving a stable higher-order grammar that makes those demonstrations progressively decodable. The complementary learner hypothesis is that a good learner is not the system that finds the greatest number of patterns in a finite transcript, but the system that extracts compact invariants that survive new data, perturbation, and intervention while improving prediction of primitive future observations and execution of the target function. In the binary benchmark, the externally scored predictive task is next-bit prediction. Tokens, segments, and higher-order symbols are endogenous, context-dependent instruments that the learner may construct because they make prediction, transfer, or action more efficient; they are not privileged targets supplied by the benchmark.""",
            ),
            (
                r"""The learner updates an internal model:

$$
M_t=U_A(M_{t-1},y_t).
$$

The target is deterministic in this paper so that uncertainty about the interaction can be separated from uncertainty in the target itself.""",
                r"""The learner updates an internal model:

$$
M_t=U_A(M_{t-1},y_t).
$$

In the strict binary track, $y_t\in\{0,1\}$ and the primitive predictive objective is:

$$
-\log p_A(y_{t+1}\mid y_{1:t}).
$$

The learner may internally encode a context-dependent substring as one token, a sequence of learned tokens as a higher-order token, or no token at all. These representations are justified by their contribution to prediction and competence, not by literal agreement with a canonical segmentation. Two learners may therefore construct different registries while being functionally equivalent at the observable bit interface.

The target is deterministic in this paper so that uncertainty about the interaction can be separated from uncertainty in the target itself.""",
            ),
            (
                r"""The learner therefore learns not only $f$, but also enough of the teacher, channel, and representational protocol to identify which aspects of the transcript are relevant to $f$.""",
                r"""The learner therefore learns not only $f$, but also enough of the teacher, channel, and representational protocol to identify which aspects of the transcript are relevant to $f$. The hierarchy is: primitive observations are evidence, prediction and task competence are the externally evaluated objectives, and tokens are revisable internal instruments for reaching those objectives.""",
            ),
            (
                r"""A better learner extracts **predictive invariants**: representations that compress relevant aspects of the past, improve prediction of the future, remain stable under appropriate perturbations, and support execution or transfer.""",
                r"""A better learner extracts **predictive invariants**: representations that compress relevant aspects of the past, improve prediction of the future, remain stable under appropriate perturbations, and support execution or transfer. In a bit-level channel, next-bit prediction remains the common external interface throughout this process. Tokenization is one possible internal realization of an invariant, not a separate primitive task.""",
            ),
            (
                r"""Among learners with comparable resources, the better learner is the one that identifies the smallest stable representation sufficient for predicting future interaction and executing the target, rather than the one that achieves the greatest retrospective fit.""",
                r"""Among learners with comparable resources, the better learner is the one that identifies the smallest stable representation sufficient for predicting future interaction and executing the target, rather than the one that achieves the greatest retrospective fit. Literal token identity is not part of this criterion: distinct registries should be treated as equivalent when they induce comparable primitive predictions, task behavior, transfer, and total representational cost.""",
            ),
            (
                r"""The first isolates structural learning. The second studies emergent coding. The third measures tolerance to arbitrary but stable conventions. The fourth introduces channel-like noise. The fifth is concealment and should not be counted as successful teaching for the specified learner.""",
                r"""The first isolates structural learning. The second studies emergent coding. The third measures tolerance to arbitrary but stable conventions. The fourth introduces channel-like noise. The fifth is concealment and should not be counted as successful teaching for the specified learner. Exact recovery of any one identifier system is a diagnostic only; the primary comparison is whether the induced representation improves prediction and target competence at the primitive observation interface.""",
            ),
            (
                r"""For small deterministic function classes, exhaustively search teacher messages under fixed learners. Measure message length, policy complexity, competence threshold, and decodability profile. Test whether optimal messages exhibit staged structure rather than opaque one-shot encodings.""",
                r"""For small deterministic function classes, exhaustively search teacher messages under fixed learners. Use the same primitive next-observation or next-bit scoring interface for all learner representations. Measure message length, policy complexity, competence threshold, and decodability profile. Test whether optimal messages exhibit staged structure rather than opaque one-shot encodings, and whether different internal token systems can achieve equivalent observable competence.""",
            ),
            (
                r"""**H4 — Predictive invariance.** Held-out prediction, transfer, and intervention stability will distinguish genuine learned structure from in-sample compression better than description length alone.""",
                r"""**H4 — Predictive and representational invariance.** Held-out primitive prediction, transfer, and intervention stability will distinguish genuine learned structure from in-sample compression better than description length alone. Distinct token registries that preserve these quantities should be functionally equivalent even when their boundaries and identifiers disagree.""",
            ),
            (
                r"""The framework is also compatible with self-tokenizing teaching: learning a registry or code is one form of reducing opacity, and later token reuse is a concrete mechanism by which previously transmitted structure can become increasingly accessible.""",
                r"""The framework is also compatible with self-tokenizing teaching: learning a registry or code is one form of reducing opacity, and later token reuse is a concrete mechanism by which previously transmitted structure can become increasingly accessible. The primitive prediction substrate need not change when the symbolic scale changes; a learner may continue predicting the next bit while using whatever context-adapted hierarchy of tokens best supports that prediction and the target task.""",
            ),
            (
                r"""> Optimal pedagogy is structured irregularity made progressively decodable; optimal learning is the extraction of predictive invariants from the mixture of signal, opacity, and noise.""",
                r"""> Optimal pedagogy is structured irregularity made progressively decodable; optimal learning is the extraction of predictive invariants from the mixture of signal, opacity, and noise. Primitive observations supply the evidence, while tokens are adaptive instruments whose value is earned by future prediction and competence.""",
            ),
        ],
        "paper: make primitive prediction and adaptive tokenization explicit",
        remove_paths=(".github/workflows/clarify-bit-substrate-241.yml",),
    )

    # Remove the temporary runner from the default branch after all target branches
    # have been updated. If branch protection rejects this final push, the paper
    # revisions remain committed and the file can be removed manually.
    run("git", "fetch", "origin", "main")
    run("git", "checkout", "-B", "main", "origin/main")
    for temporary in (
        "scripts/temporary_revise_bit_substrate_papers.py",
        ".github/workflows/temporary-paper-revision-runner.yml",
    ):
        target = REPO / temporary
        if target.exists():
            target.unlink()
    run("git", "add", "-A")
    run("git", "commit", "-m", "chore: remove temporary paper revision runner")
    run("git", "push", "origin", "HEAD:refs/heads/main")


if __name__ == "__main__":
    main()
