namespace InterventionalLatentGraph

universe u v w

/-- A binary intervention has exactly two operational arms. -/
inductive Arm where
  | zero
  | one
  deriving DecidableEq, Repr

/-- An alphabet supports a non-trivial contrast when it contains two distinct values. -/
def NontrivialContrast (α : Type u) : Prop :=
  ∃ a b : α, a ≠ b

/-- The two-arm alphabet supports a non-trivial contrast. -/
theorem arm_supports_nontrivial_contrast :
    NontrivialContrast Arm := by
  refine ⟨Arm.zero, Arm.one, ?_⟩
  intro h
  cases h

/-- A subsingleton alphabet cannot support any non-trivial intervention contrast. -/
theorem subsingleton_cannot_support_nontrivial_contrast
    (α : Type u) [Subsingleton α] :
    ¬ NontrivialContrast α := by
  intro h
  rcases h with ⟨a, b, hab⟩
  exact hab (Subsingleton.elim a b)

/--
An interventional latent graph.

The intervention type is itself the edge type: the endpoint map merely says
which two latent spaces a given intervention connects. No response agreement,
metric alignment, or equivalence is built into the graph.
-/
structure Graph (Space : Type u) (Intervention : Type v) where
  endpoints : Intervention → Space × Space

namespace Graph

/-- By definition, edges are interventions rather than separately labelled objects. -/
abbrev Edge {Space : Type u} {Intervention : Type v}
    (_G : Graph Space Intervention) : Type v :=
  Intervention

def source {Space : Type u} {Intervention : Type v}
    (G : Graph Space Intervention) (i : G.Edge) : Space :=
  (G.endpoints i).1

def target {Space : Type u} {Intervention : Type v}
    (G : Graph Space Intervention) (i : G.Edge) : Space :=
  (G.endpoints i).2

/-- Connectivity is symmetric at the primitive layer. Endpoint order carries no causal claim. -/
def Connects {Space : Type u} {Intervention : Type v}
    (G : Graph Space Intervention)
    (i : G.Edge)
    (a b : Space) : Prop :=
  G.endpoints i = (a, b) ∨ G.endpoints i = (b, a)

theorem connects_symm {Space : Type u} {Intervention : Type v}
    (G : Graph Space Intervention)
    (i : G.Edge)
    (a b : Space) :
    G.Connects i a b → G.Connects i b a := by
  intro h
  cases h with
  | inl hab => exact Or.inr hab
  | inr hba => exact Or.inl hba

/-- A walk is a composable sequence of intervention-edges. -/
inductive Walk {Space : Type u} {Intervention : Type v}
    (G : Graph Space Intervention) : Space → Space → Type (max u v) where
  | nil (a : Space) : Walk G a a
  | cons {a b c : Space}
      (i : G.Edge)
      (h : G.Connects i a b)
      (rest : Walk G b c) :
      Walk G a c

namespace Walk

def length {Space : Type u} {Intervention : Type v}
    {G : Graph Space Intervention} {a b : Space} :
    Walk G a b → Nat
  | .nil _ => 0
  | .cons _ _ rest => Nat.succ rest.length

def append {Space : Type u} {Intervention : Type v}
    {G : Graph Space Intervention} {a b c : Space} :
    Walk G a b → Walk G b c → Walk G a c
  | .nil _, q => q
  | .cons i h rest, q => .cons i h (append rest q)

theorem length_append {Space : Type u} {Intervention : Type v}
    {G : Graph Space Intervention} {a b c : Space}
    (p : Walk G a b) (q : Walk G b c) :
    (append p q).length = p.length + q.length := by
  induction p with
  | nil =>
      rfl
  | cons i h rest ih =>
      simp [append, length, ih]

end Walk

/--
Responses are deliberately outside Graph: a valid edge does not assert that
its endpoint spaces respond in the same way.
-/
structure ResponseSystem {Space : Type u} {Intervention : Type v}
    (G : Graph Space Intervention) (Observation : Type w) where
  response : Space → G.Edge → Arm → Observation

def AgreesOn {Space : Type u} {Intervention : Type v} {Observation : Type w}
    {G : Graph Space Intervention}
    (R : ResponseSystem G Observation)
    (i : G.Edge) (a b : Space) : Prop :=
  R.response a i Arm.zero = R.response b i Arm.zero ∧
  R.response a i Arm.one = R.response b i Arm.one

end Graph

/-! ## Parallel-edge witness -/

inductive PairSpace where
  | left
  | right
  deriving DecidableEq, Repr

inductive ParallelIntervention where
  | first
  | second
  deriving DecidableEq, Repr

def parallelGraph : Graph PairSpace ParallelIntervention where
  endpoints
    | .first => (.left, .right)
    | .second => (.left, .right)

theorem distinct_interventions_can_share_endpoints :
    ParallelIntervention.first ≠ ParallelIntervention.second ∧
    parallelGraph.endpoints ParallelIntervention.first =
      parallelGraph.endpoints ParallelIntervention.second := by
  constructor
  · intro h
    cases h
  · rfl

/-! ## Edge existence does not force response agreement -/

inductive SingleIntervention where
  | flip
  deriving DecidableEq, Repr

def disagreementGraph : Graph PairSpace SingleIntervention where
  endpoints
    | .flip => (.left, .right)

def oppositeResponses : Graph.ResponseSystem disagreementGraph Bool where
  response
    | .left, .flip, .zero => false
    | .left, .flip, .one => true
    | .right, .flip, .zero => true
    | .right, .flip, .one => false

theorem disagreement_edge_exists :
    disagreementGraph.Connects SingleIntervention.flip PairSpace.left PairSpace.right := by
  exact Or.inl rfl

theorem edge_does_not_force_response_agreement :
    ¬ Graph.AgreesOn oppositeResponses SingleIntervention.flip
      PairSpace.left PairSpace.right := by
  intro h
  cases h.1

/-! ## A closed three-edge walk -/

inductive TriSpace where
  | a
  | b
  | c
  deriving DecidableEq, Repr

inductive TriIntervention where
  | ab
  | bc
  | ca
  deriving DecidableEq, Repr

def triangleGraph : Graph TriSpace TriIntervention where
  endpoints
    | .ab => (.a, .b)
    | .bc => (.b, .c)
    | .ca => (.c, .a)

theorem triangle_ab :
    triangleGraph.Connects TriIntervention.ab TriSpace.a TriSpace.b := by
  exact Or.inl rfl

theorem triangle_bc :
    triangleGraph.Connects TriIntervention.bc TriSpace.b TriSpace.c := by
  exact Or.inl rfl

theorem triangle_ca :
    triangleGraph.Connects TriIntervention.ca TriSpace.c TriSpace.a := by
  exact Or.inl rfl

def triangleCycle : Graph.Walk triangleGraph TriSpace.a TriSpace.a :=
  .cons TriIntervention.ab triangle_ab
    (.cons TriIntervention.bc triangle_bc
      (.cons TriIntervention.ca triangle_ca
        (.nil TriSpace.a)))

theorem triangle_cycle_has_three_interventions :
    triangleCycle.length = 3 := by
  rfl

end InterventionalLatentGraph

#print axioms InterventionalLatentGraph.arm_supports_nontrivial_contrast
#print axioms InterventionalLatentGraph.subsingleton_cannot_support_nontrivial_contrast
#print axioms InterventionalLatentGraph.Graph.connects_symm
#print axioms InterventionalLatentGraph.Graph.Walk.length_append
#print axioms InterventionalLatentGraph.distinct_interventions_can_share_endpoints
#print axioms InterventionalLatentGraph.edge_does_not_force_response_agreement
#print axioms InterventionalLatentGraph.triangle_cycle_has_three_interventions
