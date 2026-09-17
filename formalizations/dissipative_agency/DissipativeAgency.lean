/-!
# Scale-Invariant Recursive Agency

A small Lean 4 core for the ontology used by
`sparse_intelligence_dissipative_universe.md`.

This file intentionally has no Mathlib dependency.  Physical scalars,
dynamics, coarse-graining and response measurements are abstract interfaces;
theorems below state structural consequences of the ontology relative to
those interfaces.
-/

/-- Abstract scalar used for thresholds, energy, age, distances and volumes. -/
axiom Scalar : Type

/-- Strict and non-strict scalar order supplied by a concrete model. -/
axiom scalarLT : Scalar → Scalar → Prop
axiom scalarLE : Scalar → Scalar → Prop
axiom scalarZero : Scalar
axiom nonPositive : Scalar → Prop

/-- Scale-invariant interface dimensions. -/
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
This structure alone does not certify agency.
-/
structure Assembly (α : Type) where
  members : List α
  nonempty : members ≠ []
  controller : Controller

/-- Fixed-dimensional coarse-graining shared across all substrate scales. -/
axiom phi {α : Type} (members : List α) (h : members ≠ []) : MacroState

/-- Physical organization observable.  Useful for lifecycle gates, not agency itself. -/
axiom coherence {α : Type} : List α → Scalar

/-- Universe lifecycle parameters with a mandatory hysteresis gap. -/
structure UniverseParams where
  thetaBirth : Scalar
  thetaDeath : Scalar
  tauBirth : Nat
  tauDeath : Nat
  hysteresis : scalarLT thetaDeath thetaBirth

/-- Current viability certificate for a candidate assembly. -/
def Alive {α : Type} (P : UniverseParams) (a : Assembly α) : Prop :=
  scalarLT P.thetaDeath (coherence a.members) ∧
  scalarLT scalarZero a.controller.energy

/--
An entity is organization plus a proof that its current lifecycle constraints
are satisfied.  `Entity` does not yet assert the stronger counterfactual
agency certificate below.
-/
structure Entity (P : UniverseParams) (α : Type) extends Assembly α where
  alive : Alive P toAssembly

/--
Turtles all the way up: what survives at level `k` becomes the matter from
which level `k+1` entities are constructed.
-/
def Level (P : UniverseParams) : Nat → Type
  | 0 => Primitive
  | k + 1 => Entity P (Level P k)

/-- One-step physical dynamics under optional downward control and fixed noise. -/
axiom step {α : Type} :
  List α → Option ControlSignal → Noise → List α

/--
A scalar measure of the accessible future bundle from a state under an
optional control channel and a specified exogenous disturbance.
-/
axiom ReachableVolume {α : Type} :
  List α → Option ControlSignal → Noise → Scalar

/--
Strict predictive agency is paired counterfactual future pruning: holding the
initial matter and exogenous disturbance fixed, the controlled branch reaches
a strictly smaller future volume than the free branch.
-/
def HasContrafactualAgency {α : Type}
    (members : List α)
    (c : ControlSignal)
    (ξ : Noise) : Prop :=
  scalarLT
    (ReachableVolume (step members (some c) ξ) (some c) ξ)
    (ReachableVolume (step members none ξ) none ξ)

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

/-- Abstract response fingerprint under standardized perturbations. -/
axiom CausalSignature : Type
axiom causalSignature {P : UniverseParams} {α : Type} :
  Entity P α → CausalSignature
axiom causalDistance : CausalSignature → CausalSignature → Scalar

/--
Material disjointness is abstracted from the concrete membership container so
the ontology does not require decidable equality for every substrate type.
-/
axiom DisjointMembers {α : Type} : List α → List α → Prop

/--
Full thermodynamic Ship-of-Theseus persistence: both constituent matter and
the controller instance have been replaced, while the intervention-defined
causal signature remains within tolerance.
-/
def FullTheseusPersistence {P : UniverseParams} {α : Type}
    (ε : Scalar)
    (initial current : Entity P α) : Prop :=
  DisjointMembers initial.members current.members ∧
  initial.controller.id ≠ current.controller.id ∧
  scalarLT
    (causalDistance (causalSignature initial) (causalSignature current))
    ε

/-- Viability is guaranteed by the `Entity` constructor. -/
theorem entity_viable {P : UniverseParams} {α : Type} (e : Entity P α) :
    scalarLT P.thetaDeath (coherence e.members) ∧
    scalarLT scalarZero e.controller.energy := by
  exact e.alive

/-- The recursive ontology is definitional: the next level is made of entities of this level. -/
theorem level_succ_is_entity (P : UniverseParams) (k : Nat) :
    Level P (k + 1) = Entity P (Level P k) := by
  rfl

/-- Agency certification uses exactly the same exogenous disturbance in both branches. -/
theorem agency_is_paired_counterfactual {α : Type}
    (members : List α) (c : ControlSignal) (ξ : Noise)
    (h : HasContrafactualAgency members c ξ) :
    scalarLT
      (ReachableVolume (step members (some c) ξ) (some c) ξ)
      (ReachableVolume (step members none ξ) none ξ) := by
  exact h

/-- Full Theseus persistence explicitly permits controller replacement. -/
theorem full_theseus_replaces_controller
    {P : UniverseParams} {α : Type}
    {ε : Scalar} {initial current : Entity P α}
    (h : FullTheseusPersistence ε initial current) :
    initial.controller.id ≠ current.controller.id := by
  exact h.2.1

#print axioms entity_viable
#print axioms level_succ_is_entity
#print axioms agency_is_paired_counterfactual
#print axioms full_theseus_replaces_controller
