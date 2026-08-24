namespace StructuralIdentification

universe u

/-- A family of objects of type `α`, represented intensionally. -/
abbrev Family (α : Type u) := α → Prop

/-- A truth-valued test on candidate models. -/
abbrev Query (Model : Type u) := Model → Prop

/-- Predicate inclusion without importing a set library. -/
def Subset {α : Type u} (A B : Family α) : Prop :=
  ∀ x, A x → B x

/-- Candidates in `H` that satisfy every observed truth in `E`. -/
def VersionSpace {Model : Type u}
    (H : Family Model) (E : Family (Query Model)) : Family Model :=
  fun m => H m ∧ ∀ q, E q → q m

/-- Every item of evidence is true of the target. -/
def SoundAt {Model : Type u}
    (a : Model) (E : Family (Query Model)) : Prop :=
  ∀ q, E q → q a

/-- `E` identifies `a` within `H` up to the relation `r`. -/
def Identifies {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (E : Family (Query Model)) : Prop :=
  H a ∧ SoundAt a E ∧ ∀ m, VersionSpace H E m → r m a

/-- A candidate is a genuine competitor when it lies in `H` and is not
    structurally equivalent to the target. `E` hits every competitor when
    some observed truth excludes each such candidate. -/
def HitsCompetitors {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (E : Family (Query Model)) : Prop :=
  ∀ m, H m → ¬ r m a → ∃ q, E q ∧ ¬ q m

/-- All admissible truths that hold at the target. -/
def FullEvidence {Model : Type u}
    (Q : Family (Query Model))
    (a : Model) : Family (Query Model) :=
  fun q => Q q ∧ q a

/-- The admissible query family separates the target from every
    non-equivalent competitor. -/
def SeparatesTarget {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (Q : Family (Query Model))
    (a : Model) : Prop :=
  ∀ m, H m → ¬ r m a → ∃ q, Q q ∧ q a ∧ ¬ q m

/-- Two models are observationally equivalent for a query family when every
    admissible truth has the same truth value on both. -/
def ObservationallyEquivalent {Model : Type u}
    (Q : Family (Query Model))
    (a b : Model) : Prop :=
  ∀ q, Q q → (q a ↔ q b)

/-- A query is invariant under the intended structural equivalence. -/
def QueryInvariant {Model : Type u}
    (r : Model → Model → Prop)
    (q : Query Model) : Prop :=
  ∀ x y, r x y → (q x ↔ q y)

/-- A hypothesis class is saturated under structural equivalence. -/
def FamilyInvariant {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model) : Prop :=
  ∀ x y, r x y → (H x ↔ H y)

/-- The target belongs to its own version space whenever the evidence is sound. -/
theorem target_in_version {Model : Type u}
    (H : Family Model) (E : Family (Query Model)) (a : Model)
    (ha : H a) (hsound : SoundAt a E) :
    VersionSpace H E a := by
  exact ⟨ha, hsound⟩

/-- Adding evidence can only shrink a version space. -/
theorem version_antitone_evidence {Model : Type u}
    (H : Family Model)
    (E F : Family (Query Model))
    (hEF : Subset E F) :
    Subset (VersionSpace H F) (VersionSpace H E) := by
  intro m hm
  exact ⟨hm.1, fun q hq => hm.2 q (hEF q hq)⟩

/-- Enlarging the hypothesis class can only enlarge a version space. -/
theorem version_monotone_hypotheses {Model : Type u}
    (H K : Family Model)
    (E : Family (Query Model))
    (hHK : Subset H K) :
    Subset (VersionSpace H E) (VersionSpace K E) := by
  intro m hm
  exact ⟨hHK m hm.1, hm.2⟩

/-- Identification in a larger hypothesis class descends to every smaller
    class that still contains the target. -/
theorem identification_descends_to_subclass {Model : Type u}
    (r : Model → Model → Prop)
    (H K : Family Model)
    (a : Model)
    (E : Family (Query Model))
    (hHK : Subset H K)
    (ha : H a)
    (hid : Identifies r K a E) :
    Identifies r H a E := by
  refine ⟨ha, hid.2.1, ?_⟩
  intro m hm
  exact hid.2.2 m ⟨hHK m hm.1, hm.2⟩

/-- Once identification has been achieved, adding further truths about the
    target preserves identification. -/
theorem identification_persists_with_more_sound_evidence {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (E F : Family (Query Model))
    (hEF : Subset E F)
    (hFsound : SoundAt a F)
    (hid : Identifies r H a E) :
    Identifies r H a F := by
  refine ⟨hid.1, hFsound, ?_⟩
  intro m hm
  exact hid.2.2 m ((version_antitone_evidence H E F hEF) m hm)

/-- If `r` is refined to a weaker identification criterion `s`, any certificate
    for `r` is automatically a certificate for `s`. -/
theorem identification_relaxes_equivalence {Model : Type u}
    (r s : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (E : Family (Query Model))
    (hrs : ∀ x y, r x y → s x y)
    (hid : Identifies r H a E) :
    Identifies s H a E := by
  refine ⟨hid.1, hid.2.1, ?_⟩
  intro m hm
  exact hrs m a (hid.2.2 m hm)

/-- Hitting-set characterization: sound evidence identifies the target exactly
    when it excludes every non-equivalent competitor. -/
theorem identifies_iff_hits_competitors {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (E : Family (Query Model)) :
    Identifies r H a E ↔
      H a ∧ SoundAt a E ∧ HitsCompetitors r H a E := by
  classical
  constructor
  · intro hid
    refine ⟨hid.1, hid.2.1, ?_⟩
    intro m hm hne
    by_contra hnone
    have hall : ∀ q, E q → q m := by
      intro q hq
      by_contra hqm
      exact hnone ⟨q, hq, hqm⟩
    exact hne (hid.2.2 m ⟨hm, hall⟩)
  · intro h
    refine ⟨h.1, h.2.1, ?_⟩
    intro m hm
    by_contra hne
    obtain ⟨q, hqE, hnqm⟩ := h.2.2 m hm.1 hne
    exact hnqm (hm.2 q hqE)

/-- The complete admissible truth profile identifies the target exactly when
    the query family separates it from every non-equivalent competitor. -/
theorem full_evidence_identifies_iff_separates {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (Q : Family (Query Model))
    (a : Model)
    (ha : H a) :
    Identifies r H a (FullEvidence Q a) ↔
      SeparatesTarget r H Q a := by
  constructor
  · intro hid
    have hhits := (identifies_iff_hits_competitors r H a (FullEvidence Q a)).mp hid
    intro m hm hne
    obtain ⟨q, hq, hnqm⟩ := hhits.2.2 m hm hne
    exact ⟨q, hq.1, hq.2, hnqm⟩
  · intro hsep
    apply (identifies_iff_hits_competitors r H a (FullEvidence Q a)).mpr
    refine ⟨ha, ?_, ?_⟩
    · intro q hq
      exact hq.2
    · intro m hm hne
      obtain ⟨q, hqQ, hqa, hnqm⟩ := hsep m hm hne
      exact ⟨q, ⟨hqQ, hqa⟩, hnqm⟩

/-- Fundamental identifiability barrier: if a non-equivalent competitor agrees
    with the target on every admissible query, then no evidence chosen from that
    query family can identify the target. -/
theorem observational_equivalence_blocks_identification {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (Q E : Family (Query Model))
    (a b : Model)
    (hE : Subset E Q)
    (hb : H b)
    (hne : ¬ r b a)
    (hobs : ObservationallyEquivalent Q a b) :
    ¬ Identifies r H a E := by
  intro hid
  apply hne
  apply hid.2.2 b
  refine ⟨hb, ?_⟩
  intro q hqE
  exact (hobs q (hE q hqE)).mp (hid.2.1 q hqE)

/-- If both the hypothesis class and every observed query are structural
    invariants, then the version space is itself structural: it cannot split
    equivalent presentations. -/
theorem version_space_is_invariant {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (E : Family (Query Model))
    (hH : FamilyInvariant r H)
    (hE : ∀ q, E q → QueryInvariant r q) :
    ∀ x y, r x y → (VersionSpace H E x ↔ VersionSpace H E y) := by
  intro x y hxy
  constructor
  · intro hx
    refine ⟨(hH x y hxy).mp hx.1, ?_⟩
    intro q hq
    exact (hE q hq x y hxy).mp (hx.2 q hq)
  · intro hy
    refine ⟨(hH x y hxy).mpr hy.1, ?_⟩
    intro q hq
    exact (hE q hq x y hxy).mpr (hy.2 q hq)

/-- Recursive conjunction of a finite list of truth-valued queries. -/
def HoldsAll {Model : Type u} : List (Query Model) → Model → Prop
  | [], _ => True
  | q :: qs, m => q m ∧ HoldsAll qs m

/-- The single truth-valued query obtained by conjoining a finite list. -/
def Conjunction {Model : Type u}
    (qs : List (Query Model)) : Query Model :=
  fun m => HoldsAll qs m

/-- Finite-list version of identification, used to expose conjunction collapse. -/
def ListIdentifies {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (qs : List (Query Model)) : Prop :=
  H a ∧ HoldsAll qs a ∧
    ∀ m, H m → HoldsAll qs m → r m a

/-- All entries of a finite query list lie in the admissible query family. -/
def AllAdmissible {Model : Type u}
    (Q : Family (Query Model)) : List (Query Model) → Prop
  | [] => True
  | q :: qs => Q q ∧ AllAdmissible Q qs

/-- The query family admits arbitrary finite conjunctions. -/
def ClosedUnderFiniteConjunction {Model : Type u}
    (Q : Family (Query Model)) : Prop :=
  ∀ qs, AllAdmissible Q qs → Q (Conjunction qs)

/-- Conjunction collapse: any finite identifying list carries exactly the same
    identifying power as the singleton query given by its conjunction. -/
theorem conjunction_collapse {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (qs : List (Query Model)) :
    ListIdentifies r H a qs ↔
      ListIdentifies r H a [Conjunction qs] := by
  constructor
  · intro h
    refine ⟨h.1, ?_, ?_⟩
    · exact ⟨h.2.1, True.intro⟩
    · intro m hm hs
      exact h.2.2 m hm hs.1
  · intro h
    refine ⟨h.1, h.2.1.1, ?_⟩
    intro m hm hs
    exact h.2.2 m hm ⟨hs, True.intro⟩

/-- If the admissible language is closed under finite conjunction and unit cost
    counts only the number of formulas, every finite certificate collapses to a
    one-query certificate. This is why a nontrivial theory must restrict the
    query family or charge for formula complexity. -/
theorem one_query_if_closed_under_conjunction {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (Q : Family (Query Model))
    (a : Model)
    (qs : List (Query Model))
    (hclosed : ClosedUnderFiniteConjunction Q)
    (hadm : AllAdmissible Q qs)
    (hid : ListIdentifies r H a qs) :
    Q (Conjunction qs) ∧
      ListIdentifies r H a [Conjunction qs] := by
  exact ⟨hclosed qs hadm, (conjunction_collapse r H a qs).mp hid⟩

/-! ## A finite motivating example

The four named candidates reproduce the paper's running example.  `orderFour`
models the fact "there exists an element of order four"; `commutative` and
`carrierFour` add progressively stronger truths.  No algebra library is needed:
the example is about discrimination among already-classified structures, not
about reproving their group laws.
-/

inductive ToyModel where
  | c4
  | v4
  | c8
  | d4
  deriving DecidableEq

open ToyModel

def toyHypotheses : Family ToyModel := fun _ => True

def orderFour : Query ToyModel
  | c4 => True
  | v4 => False
  | c8 => True
  | d4 => True

def commutative : Query ToyModel
  | d4 => False
  | _ => True

def carrierFour : Query ToyModel
  | c4 => True
  | v4 => True
  | _ => False

def evidenceOrderFour : Family (Query ToyModel) :=
  fun q => q = orderFour

def evidenceOrderFourComm : Family (Query ToyModel) :=
  fun q => q = orderFour ∨ q = commutative

def evidenceAllThree : Family (Query ToyModel) :=
  fun q => q = orderFour ∨ q = commutative ∨ q = carrierFour

theorem c8_survives_order_four :
    VersionSpace toyHypotheses evidenceOrderFour c8 := by
  constructor
  · trivial
  · intro q hq
    cases hq
    trivial

theorem d4_survives_order_four :
    VersionSpace toyHypotheses evidenceOrderFour d4 := by
  constructor
  · trivial
  · intro q hq
    cases hq
    trivial

theorem v4_excluded_by_order_four :
    ¬ VersionSpace toyHypotheses evidenceOrderFour v4 := by
  intro h
  have hf : orderFour v4 := h.2 orderFour rfl
  exact hf

theorem d4_excluded_by_commutativity :
    ¬ VersionSpace toyHypotheses evidenceOrderFourComm d4 := by
  intro h
  have hf : commutative d4 := h.2 commutative (Or.inr rfl)
  exact hf

theorem c8_excluded_by_carrier_size :
    ¬ VersionSpace toyHypotheses evidenceAllThree c8 := by
  intro h
  have hf : carrierFour c8 := h.2 carrierFour (Or.inr (Or.inr rfl))
  exact hf

/-- The three truths isolate `C4` in this hypothesis class. -/
theorem three_truths_identify_c4 :
    Identifies (fun x y : ToyModel => x = y)
      toyHypotheses c4 evidenceAllThree := by
  refine ⟨trivial, ?_, ?_⟩
  · intro q hq
    rcases hq with h | h | h
    · cases h
      trivial
    · cases h
      trivial
    · cases h
      trivial
  · intro m hm
    cases m with
    | c4 => rfl
    | v4 =>
        have hf : orderFour v4 := hm.2 orderFour (Or.inl rfl)
        exact False.elim hf
    | c8 =>
        have hf : carrierFour c8 := hm.2 carrierFour (Or.inr (Or.inr rfl))
        exact False.elim hf
    | d4 =>
        have hf : commutative d4 := hm.2 commutative (Or.inr (Or.inl rfl))
        exact False.elim hf

end StructuralIdentification

#print axioms StructuralIdentification.identifies_iff_hits_competitors
#print axioms StructuralIdentification.observational_equivalence_blocks_identification
#print axioms StructuralIdentification.version_space_is_invariant
#print axioms StructuralIdentification.conjunction_collapse
#print axioms StructuralIdentification.three_truths_identify_c4
