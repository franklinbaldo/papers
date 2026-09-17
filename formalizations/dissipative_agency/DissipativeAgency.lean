/-!
# Scale-Consistent Recursive Agency

A small Lean 4 core for the ontology and epistemic contract used by
`sparse_intelligence_dissipative_universe.md`.

The formalization deliberately separates three questions:

1. what ideal counterfactual agency means;
2. what finite measurement contract is allowed to estimate it;
3. what empirical evidence threshold must be crossed before an agency claim
   may be issued.

This file intentionally has no Mathlib dependency. Physical scalars,
dynamics, coarse-graining, estimators, confidence procedures and response
measurements are abstract interfaces. Lean checks the logical separation and
contract-binding properties relative to those interfaces; the concrete
numerical/statistical claims remain empirical.
-/

/-- Abstract scalar used for thresholds, energy, age, distances and volumes. -/
axiom Scalar : Type

/-- Strict and non-strict scalar order supplied by a concrete model. -/
axiom scalarLT : Scalar → Scalar → Prop
axiom scalarLE : Scalar → Scalar → Prop
axiom scalarZero : Scalar
axiom nonPositive : Scalar → Prop

/-- Interface dimensions reused across the simulator-defined discrete levels. -/
axiom dMacro : Nat
axiom dControl : Nat

abbrev MacroState : Type := Fin dMacro → Scalar
abbrev ControlSignal : Type := Fin dControl → Scalar

/-- Lowest computational cutoff of a concrete simulation. -/
axiom Primitive : Type

/-- Exogenous disturbance shared by paired counterfactual branches. -/
axiom Noise : Type

/-- A replaceable implementation of the abstract intelligence operator. -/
structure Controller where
  id : Nat
  forward : MacroState → ControlSignal
  energy : Scalar
  age : Scalar

/--
Matter organized into a nonempty candidate assembly plus a controller.
This structure alone certifies neither viability nor agency.
-/
structure Assembly (α : Type) where
  members : List α
  nonempty : members ≠ []
  controller : Controller

/-- Fixed-dimensional coarse-graining reused across all substrate levels. -/
axiom phi {α : Type} (members : List α) (h : members ≠ []) : MacroState

/-- Physical organization observable. Useful for lifecycle gates, not agency itself. -/
axiom coherence {α : Type} : List α → Scalar

/-- Universe lifecycle parameters with a mandatory hysteresis gap. -/
structure UniverseParams where
  thetaBirth : Scalar
  thetaDeath : Scalar
  tauBirth : Nat
  tauDeath : Nat
  hysteresis : scalarLT thetaDeath thetaBirth

/-- Current lifecycle viability certificate for a candidate assembly. -/
def Alive {α : Type} (P : UniverseParams) (a : Assembly α) : Prop :=
  scalarLT P.thetaDeath (coherence a.members) ∧
  scalarLT scalarZero a.controller.energy

/--
An entity is organization plus a proof that its current lifecycle constraints
are satisfied. `Entity` does not assert counterfactual agency.
-/
structure Entity (P : UniverseParams) (α : Type) extends Assembly α where
  alive : Alive P toAssembly

/--
Turtles all the way up: what survives at level `k` becomes the matter from
which level `k+1` entities are constructed.

This is recursive scale-consistency across discrete simulator-defined levels;
it is not a theorem of continuous scale invariance.
-/
def Level (P : UniverseParams) : Nat → Type
  | 0 => Primitive
  | k + 1 => Entity P (Level P k)

/-- One-step physical dynamics under optional downward control and fixed noise. -/
axiom step {α : Type} :
  List α → Option ControlSignal → Noise → List α

/-! ## Ideal counterfactual agency -/

/--
A scalar idealization of the accessible future bundle from a state under an
optional control channel and specified exogenous disturbance.

This is the semantic target. It is not itself the finite estimator used by a
concrete experiment.
-/
axiom ReachableVolume {α : Type} :
  List α → Option ControlSignal → Noise → Scalar

/--
A paired counterfactual packages the shared initial matter and shared
exogenous disturbance once, so the controlled and free branches cannot be
constructed from different starting worlds without constructing a different
pair.
-/
structure PairedCounterfactual (α : Type) where
  members : List α
  nonempty : members ≠ []
  control : ControlSignal
  noise : Noise

inductive CounterfactualBranch where
  | controlled
  | free

/-- Branch-specific control derived from one paired counterfactual. -/
def branchControl (c : ControlSignal) : CounterfactualBranch → Option ControlSignal
  | .controlled => some c
  | .free => none

/-- Both branches inherit the same initial matter and the same exogenous noise. -/
def branchState {α : Type}
    (pair : PairedCounterfactual α)
    (branch : CounterfactualBranch) : List α :=
  step pair.members (branchControl pair.control branch) pair.noise

/--
Ideal predictive agency: under the same initial matter and exogenous noise,
the controlled branch has strictly smaller accessible future volume than the
free branch.
-/
def HasIdealContrafactualAgency {α : Type}
    (pair : PairedCounterfactual α) : Prop :=
  scalarLT
    (ReachableVolume
      (branchState pair .controlled)
      (branchControl pair.control .controlled)
      pair.noise)
    (ReachableVolume
      (branchState pair .free)
      (branchControl pair.control .free)
      pair.noise)

/-! ## Finite measurement contract -/

/--
Versioned finite measurement contract. A concrete preregistration supplies
one fixed instance. The contract freezes the macrostate dimension ceiling,
rollout budget, estimator identity, horizon and evidentiary threshold.
-/
structure FutureVolumeContract where
  version : Nat
  estimatorId : Nat
  rolloutCount : Nat
  primaryHorizon : Nat
  supportingHorizons : List Nat
  regularizer : Scalar
  minimumEffect : Scalar
  confidenceLevel : Scalar
  maxMacroDimension : Nat
  dimensionAdmissible : dMacro ≤ maxMacroDimension

/--
Finite rollouts are observed only through the fixed-dimensional macrostate.
The microscopic state size therefore does not appear in the certificate type.
-/
axiom rolloutMacrostate {α : Type} :
  PairedCounterfactual α →
  CounterfactualBranch →
  Nat →  -- rollout index
  Nat →  -- horizon
  MacroState

/--
The numerical estimator remains abstract. A concrete implementation is named
and frozen by `estimatorId` in the registered contract; alternative estimators
cannot inherit the same empirical certificate unless they use that contract.
-/
axiom EstimatedFutureVolume :
  FutureVolumeContract → List MacroState → Scalar

/-- Result of the finite paired experiment under one registered contract. -/
structure AgencyEstimate where
  contractVersion : Nat
  estimatorId : Nat
  rolloutCount : Nat
  horizon : Nat
  freeVolume : Scalar
  controlledVolume : Scalar
  effect : Scalar
  lowerConfidenceBound : Scalar

/--
Empirical agency is not a point-estimate inequality. The result must be bound
to the exact registered contract and its lower confidence bound must clear the
preregistered minimum meaningful effect.
-/
def PassesAgencyGate
    (contract : FutureVolumeContract)
    (estimate : AgencyEstimate) : Prop :=
  estimate.contractVersion = contract.version ∧
  estimate.estimatorId = contract.estimatorId ∧
  estimate.rolloutCount = contract.rolloutCount ∧
  estimate.horizon = contract.primaryHorizon ∧
  scalarLT contract.minimumEffect estimate.lowerConfidenceBound

/-- A first-class empirical certificate couples evidence to the frozen contract. -/
structure EmpiricalAgencyCertificate where
  contract : FutureVolumeContract
  estimate : AgencyEstimate
  passes : PassesAgencyGate contract estimate

/-! ## Lifecycle timing -/

/-- Sustained evidence above the birth threshold. -/
def SustainedAbove {α : Type}
    (P : UniverseParams)
    (trace : Nat → Assembly α)
    (t0 duration : Nat) : Prop :=
  ∀ dt, dt < duration →
    scalarLE P.thetaBirth (coherence (trace (t0 + dt)).members)

/-- Sustained evidence below the death threshold. -/
def SustainedBelow {α : Type}
    (P : UniverseParams)
    (trace : Nat → Assembly α)
    (t0 duration : Nat) : Prop :=
  ∀ dt, dt < duration →
    scalarLT (coherence (trace (t0 + dt)).members) P.thetaDeath

/-- Birth is temporal, not a one-frame fluctuation. -/
def CanSpawn {α : Type}
    (P : UniverseParams)
    (trace : Nat → Assembly α)
    (t0 : Nat) : Prop :=
  SustainedAbove P trace t0 P.tauBirth

/-- A current entity must dissolve if its energy budget is non-positive. -/
def EnergyForcesDissolution {P : UniverseParams} {α : Type}
    (e : Entity P α) : Prop :=
  nonPositive e.controller.energy

/-! ## Causal identity and full Theseus persistence -/

/-- Abstract response fingerprint under a standardized perturbation battery. -/
axiom CausalSignature : Type

/--
Versioned identity contract freezes the tolerance and intervention surface
before turnover outcomes are inspected.
-/
structure CausalIdentityContract where
  version : Nat
  signatureId : Nat
  epsilon : Scalar
  perturbationCount : Nat
  responseHorizon : Nat

axiom causalSignature {P : UniverseParams} {α : Type} :
  CausalIdentityContract → Entity P α → CausalSignature

axiom causalDistance : CausalSignature → CausalSignature → Scalar

/--
Material disjointness is abstracted from the concrete membership container so
the ontology does not require decidable equality for every substrate type.
-/
axiom DisjointMembers {α : Type} : List α → List α → Prop

/--
Full thermodynamic Ship-of-Theseus persistence: both constituent matter and
the controller instance have been replaced, while the response signature
remains within the tolerance of the same frozen identity contract.
-/
def FullTheseusPersistence {P : UniverseParams} {α : Type}
    (contract : CausalIdentityContract)
    (initial current : Entity P α) : Prop :=
  DisjointMembers initial.members current.members ∧
  initial.controller.id ≠ current.controller.id ∧
  scalarLT
    (causalDistance
      (causalSignature contract initial)
      (causalSignature contract current))
    contract.epsilon

/-! ## Structural theorems -/

/-- Viability is guaranteed by the `Entity` constructor. -/
theorem entity_viable {P : UniverseParams} {α : Type} (e : Entity P α) :
    scalarLT P.thetaDeath (coherence e.members) ∧
    scalarLT scalarZero e.controller.energy := by
  exact e.alive

/-- The recursive ontology is definitional: the next level is made of entities of this level. -/
theorem level_succ_is_entity (P : UniverseParams) (k : Nat) :
    Level P (k + 1) = Entity P (Level P k) := by
  rfl

/-- Ideal agency is necessarily paired on the same encoded world. -/
theorem ideal_agency_is_paired {α : Type}
    (pair : PairedCounterfactual α)
    (h : HasIdealContrafactualAgency pair) :
    scalarLT
      (ReachableVolume
        (branchState pair .controlled)
        (branchControl pair.control .controlled)
        pair.noise)
      (ReachableVolume
        (branchState pair .free)
        (branchControl pair.control .free)
        pair.noise) := by
  exact h

/-- An empirical certificate cannot silently switch contract versions. -/
theorem empirical_certificate_uses_registered_version
    (cert : EmpiricalAgencyCertificate) :
    cert.estimate.contractVersion = cert.contract.version := by
  exact cert.passes.1

/-- An empirical certificate clears the registered minimum meaningful effect. -/
theorem empirical_certificate_clears_minimum_effect
    (cert : EmpiricalAgencyCertificate) :
    scalarLT cert.contract.minimumEffect cert.estimate.lowerConfidenceBound := by
  exact cert.passes.2.2.2.2

/-- Full Theseus persistence explicitly requires controller replacement. -/
theorem full_theseus_replaces_controller
    {P : UniverseParams} {α : Type}
    {contract : CausalIdentityContract}
    {initial current : Entity P α}
    (h : FullTheseusPersistence contract initial current) :
    initial.controller.id ≠ current.controller.id := by
  exact h.2.1

#print axioms entity_viable
#print axioms level_succ_is_entity
#print axioms ideal_agency_is_paired
#print axioms empirical_certificate_uses_registered_version
#print axioms empirical_certificate_clears_minimum_effect
#print axioms full_theseus_replaces_controller
