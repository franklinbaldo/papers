namespace SemanticObservers

universe u v w s d

abbrev Family (α : Type u) := α → Prop

def Subset {α : Type u} (A B : Family α) : Prop :=
  ∀ x, A x → B x

/-! ## Deterministic experiments and exact garbling -/

/-- `B` is an exact deterministic garbling of `A` when one total map on the
observation space of `A` reproduces `B` for every indexed state. -/
def DeterministicGarbling
    {Θ : Type u} {ZA : Type v} {ZB : Type w}
    (A : Θ → ZA) (B : Θ → ZB) : Prop :=
  ∃ g : ZA → ZB, ∀ θ, g (A θ) = B θ

/-- The fibers of `A` refine the fibers of `B`: whenever `A` identifies two
states, `B` must identify them as well. -/
def FiberRefines
    {Θ : Type u} {ZA : Type v} {ZB : Type w}
    (A : Θ → ZA) (B : Θ → ZB) : Prop :=
  ∀ x y, A x = A y → B x = B y

theorem deterministicGarbling_implies_fiberRefines
    {Θ : Type u} {ZA : Type v} {ZB : Type w}
    (A : Θ → ZA) (B : Θ → ZB)
    (h : DeterministicGarbling A B) :
    FiberRefines A B := by
  rcases h with ⟨g, hg⟩
  intro x y hxy
  calc
    B x = g (A x) := (hg x).symm
    _ = g (A y) := congrArg g hxy
    _ = B y := hg y

/-- With a nonempty target observation type, fiber refinement is also
sufficient for an exact deterministic garbling. Outside the range of `A`, the
simulator may return an arbitrary fallback value. -/
theorem deterministicGarbling_iff_fiberRefines
    {Θ : Type u} {ZA : Type v} {ZB : Type w}
    [Nonempty ZB]
    (A : Θ → ZA) (B : Θ → ZB) :
    DeterministicGarbling A B ↔ FiberRefines A B := by
  constructor
  · exact deterministicGarbling_implies_fiberRefines A B
  · intro href
    classical
    let fallback : ZB := Classical.choice (inferInstance : Nonempty ZB)
    let g : ZA → ZB := fun z =>
      if hz : ∃ θ, A θ = z then
        B (Classical.choose hz)
      else
        fallback
    refine ⟨g, ?_⟩
    intro θ
    dsimp [g]
    split
    · next hz =>
        have hchosen : A (Classical.choose hz) = A θ :=
          Classical.choose_spec hz
        exact href (Classical.choose hz) θ hchosen
    · next hz =>
        exact False.elim (hz ⟨θ, rfl⟩)

/-- If the source observation is injective on the indexed states, an
unrestricted deterministic garbling can reproduce any target observation. -/
theorem injective_source_simulates_any
    {Θ : Type u} {ZA : Type v} {ZB : Type w}
    [Nonempty ZB]
    (A : Θ → ZA) (B : Θ → ZB)
    (hA : Function.Injective A) :
    DeterministicGarbling A B := by
  apply (deterministicGarbling_iff_fiberRefines A B).2
  intro x y hxy
  exact congrArg B (hA hxy)

/-- If two deterministic encoders are both injective on the registered
benchmark, unrestricted exact garblings exist in both directions. -/
theorem injective_encoders_are_bilaterally_garbling
    {Θ : Type u} {ZA : Type v} {ZB : Type w}
    [Nonempty ZA] [Nonempty ZB]
    (A : Θ → ZA) (B : Θ → ZB)
    (hA : Function.Injective A)
    (hB : Function.Injective B) :
    DeterministicGarbling A B ∧ DeterministicGarbling B A := by
  exact ⟨injective_source_simulates_any A B hA,
    injective_source_simulates_any B A hB⟩

/-- A collision in `A` that `B` resolves blocks exact simulation from `A` to
`B`. This is the deterministic form of information loss. -/
theorem resolved_collision_blocks_garbling
    {Θ : Type u} {ZA : Type v} {ZB : Type w}
    (A : Θ → ZA) (B : Θ → ZB)
    (x y : Θ)
    (hA : A x = A y)
    (hB : B x ≠ B y) :
    ¬ DeterministicGarbling A B := by
  intro h
  apply hB
  exact (deterministicGarbling_implies_fiberRefines A B h) x y hA

/-! ## Restricted decision orders -/

/-- Empirical dominance relative to one registered family of decision
problems and one externally supplied risk functional. -/
def RestrictedDominates
    {Observer : Type u} {Decision : Type v} {Score : Type w}
    [LE Score]
    (risk : Observer → Decision → Score)
    (D : Family Decision)
    (A B : Observer) : Prop :=
  ∀ d, D d → risk A d ≤ risk B d

/-- Dominance on a larger decision family implies dominance on every
subfamily. The converse is not valid in general. -/
theorem restrictedDominance_descends
    {Observer : Type u} {Decision : Type v} {Score : Type w}
    [LE Score]
    (risk : Observer → Decision → Score)
    (D E : Family Decision)
    (A B : Observer)
    (hDE : Subset D E)
    (h : RestrictedDominates risk E A B) :
    RestrictedDominates risk D A B := by
  intro d hd
  exact h d (hDE d hd)

/-! ### A finite order-reversal counterexample -/

/-- Toy risk: an observer is perfect on the decision carrying the same Boolean
index and incurs unit risk on the other decision. -/
def toyRisk (observer decision : Bool) : Nat :=
  if observer = decision then 0 else 1

def OnlyFalse : Family Bool := fun d => d = false
def OnlyTrue : Family Bool := fun d => d = true

theorem toy_false_dominates_on_false :
    RestrictedDominates toyRisk OnlyFalse false true := by
  intro d hd
  subst d
  decide

theorem toy_true_dominates_on_true :
    RestrictedDominates toyRisk OnlyTrue true false := by
  intro d hd
  subst d
  decide

theorem toy_false_does_not_dominate_on_true :
    ¬ RestrictedDominates toyRisk OnlyTrue false true := by
  intro h
  have hbad := h true rfl
  decide at hbad

theorem toy_true_does_not_dominate_on_false :
    ¬ RestrictedDominates toyRisk OnlyFalse true false := by
  intro h
  have hbad := h false rfl
  decide at hbad

/-- Dominance on one decision family can reverse on a disjoint family. This
is why a single restricted order cannot by itself support an observer-level
claim. -/
theorem disjoint_decision_families_can_reverse_order :
    RestrictedDominates toyRisk OnlyFalse false true ∧
    RestrictedDominates toyRisk OnlyTrue true false ∧
    ¬ RestrictedDominates toyRisk OnlyTrue false true ∧
    ¬ RestrictedDominates toyRisk OnlyFalse true false := by
  exact ⟨toy_false_dominates_on_false,
    toy_true_dominates_on_true,
    toy_false_does_not_dominate_on_true,
    toy_true_does_not_dominate_on_false⟩

/-! ## Reparameterization and probe-class dependence -/

abbrev Rule (Z : Type u) (Action : Type v) := Z → Action

/-- Pull a decision rule on `W` back through an invertible coordinate change
`φ : Z ≃ W`. -/
def pullRule
    {Z : Type u} {W : Type v} {Action : Type w}
    (φ : Z ≃ W) (q : Rule W Action) : Rule Z Action :=
  fun z => q (φ z)

/-- Push a rule on `Z` forward through an invertible coordinate change. -/
def pushRule
    {Z : Type u} {W : Type v} {Action : Type w}
    (φ : Z ≃ W) (q : Rule Z Action) : Rule W Action :=
  fun w => q (φ.symm w)

theorem pull_push_rule
    {Z : Type u} {W : Type v} {Action : Type w}
    (φ : Z ≃ W) (q : Rule Z Action) :
    pullRule φ (pushRule φ q) = q := by
  funext z
  simp [pullRule, pushRule]

theorem push_pull_rule
    {Z : Type u} {W : Type v} {Action : Type w}
    (φ : Z ≃ W) (q : Rule W Action) :
    pushRule φ (pullRule φ q) = q := by
  funext w
  simp [pullRule, pushRule]

/-- An attained optimum for an unrestricted or restricted rule class. -/
def IsOptimal
    {RuleType : Type u} {Score : Type v}
    [LE Score]
    (admissible : Family RuleType)
    (eval : RuleType → Score)
    (q : RuleType) : Prop :=
  admissible q ∧ ∀ r, admissible r → eval q ≤ eval r

/-- The transformed evaluator measures a rule after pulling it back to the
original observation coordinates. -/
def reparamEval
    {Z : Type u} {W : Type v} {Action : Type w} {Score : Type s}
    (φ : Z ≃ W)
    (evalZ : Rule Z Action → Score)
    (qW : Rule W Action) : Score :=
  evalZ (pullRule φ qW)

/-- Two probe classes correspond under an invertible reparameterization when
pullback and pushforward preserve admissibility. -/
def ProbeClassesCorrespond
    {Z : Type u} {W : Type v} {Action : Type w}
    (φ : Z ≃ W)
    (HZ : Family (Rule Z Action))
    (HW : Family (Rule W Action)) : Prop :=
  (∀ qW, HW qW → HZ (pullRule φ qW)) ∧
  (∀ qZ, HZ qZ → HW (pushRule φ qZ))

/-- A restricted optimum transports through an invertible coordinate change
provided the probe classes themselves correspond under that change. -/
theorem optimal_rule_transports_under_corresponding_probe_classes
    {Z : Type u} {W : Type v} {Action : Type w} {Score : Type s}
    [Preorder Score]
    (φ : Z ≃ W)
    (HZ : Family (Rule Z Action))
    (HW : Family (Rule W Action))
    (evalZ : Rule Z Action → Score)
    (qZ : Rule Z Action)
    (hclasses : ProbeClassesCorrespond φ HZ HW)
    (hopt : IsOptimal HZ evalZ qZ) :
    IsOptimal HW (reparamEval φ evalZ) (pushRule φ qZ) := by
  constructor
  · exact hclasses.2 qZ hopt.1
  · intro rW hrW
    have hrZ : HZ (pullRule φ rW) := hclasses.1 rW hrW
    have hle := hopt.2 (pullRule φ rW) hrZ
    simpa [reparamEval, pull_push_rule] using hle

/-- If both restricted problems attain optima and their probe classes
correspond, the optimal values agree exactly after reparameterization. -/
theorem optimal_values_invariant_under_corresponding_probe_classes
    {Z : Type u} {W : Type v} {Action : Type w} {Score : Type s}
    [PartialOrder Score]
    (φ : Z ≃ W)
    (HZ : Family (Rule Z Action))
    (HW : Family (Rule W Action))
    (evalZ : Rule Z Action → Score)
    (qZ : Rule Z Action)
    (qW : Rule W Action)
    (hclasses : ProbeClassesCorrespond φ HZ HW)
    (hoptZ : IsOptimal HZ evalZ qZ)
    (hoptW : IsOptimal HW (reparamEval φ evalZ) qW) :
    evalZ qZ = reparamEval φ evalZ qW := by
  apply le_antisymm
  · have hqWZ : HZ (pullRule φ qW) := hclasses.1 qW hoptW.1
    exact hoptZ.2 (pullRule φ qW) hqWZ
  · have htransport :=
      optimal_rule_transports_under_corresponding_probe_classes
        φ HZ HW evalZ qZ hclasses hoptZ
    have hle := hoptW.2 (pushRule φ qZ) htransport.1
    simpa [reparamEval, pull_push_rule] using hle

/-! ### Concrete counterexample: invertible information, non-invariant probe -/

def boolNotEquiv : Bool ≃ Bool where
  toFun := Bool.not
  invFun := Bool.not
  left_inv := by
    intro b
    cases b <;> rfl
  right_inv := by
    intro b
    cases b <;> rfl

/-- A deliberately tiny probe class containing only the identity rule. -/
def IdentityProbe : Family (Rule Bool Bool) :=
  fun q => q = id

/-- Zero-one loss over the two Boolean states for recovering the original
state label. -/
def boolIdentityLoss (q : Rule Bool Bool) : Nat :=
  (if q false = false then 0 else 1) +
  (if q true = true then 0 else 1)

theorem identity_probe_perfect_before_reparameterization :
    boolIdentityLoss id = 0 := by
  rfl

theorem identity_probe_fails_after_not_reparameterization :
    reparamEval boolNotEquiv boolIdentityLoss id = 2 := by
  rfl

/-- A wild-enough invertible coordinate change can alter restricted-probe
extractability even though unrestricted decision information is preserved.
The missing hypothesis is probe-class correspondence/equivariance. -/
theorem invertible_reparameterization_need_not_preserve_fixed_probe_score :
    boolIdentityLoss id ≠ reparamEval boolNotEquiv boolIdentityLoss id := by
  decide

#print axioms deterministicGarbling_iff_fiberRefines
#print axioms injective_encoders_are_bilaterally_garbling
#print axioms disjoint_decision_families_can_reverse_order
#print axioms optimal_values_invariant_under_corresponding_probe_classes
#print axioms invertible_reparameterization_need_not_preserve_fixed_probe_score

end SemanticObservers
