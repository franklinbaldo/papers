namespace StructuralIdentification

universe u

abbrev Family (α : Type u) := α → Prop
abbrev Query (Model : Type u) := Model → Prop

def Subset {α : Type u} (A B : Family α) : Prop :=
  ∀ x, A x → B x

def VersionSpace {Model : Type u}
    (H : Family Model) (E : Family (Query Model)) : Family Model :=
  fun m => H m ∧ ∀ q, E q → q m

def SoundAt {Model : Type u}
    (a : Model) (E : Family (Query Model)) : Prop :=
  ∀ q, E q → q a

def Identifies {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (E : Family (Query Model)) : Prop :=
  H a ∧ SoundAt a E ∧ ∀ m, VersionSpace H E m → r m a

def HitsCompetitors {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (E : Family (Query Model)) : Prop :=
  ∀ m, H m → ¬ r m a → ∃ q, E q ∧ ¬ q m

def FullEvidence {Model : Type u}
    (Q : Family (Query Model))
    (a : Model) : Family (Query Model) :=
  fun q => Q q ∧ q a

def SeparatesTarget {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (Q : Family (Query Model))
    (a : Model) : Prop :=
  ∀ m, H m → ¬ r m a → ∃ q, Q q ∧ q a ∧ ¬ q m

def ObservationallyEquivalent {Model : Type u}
    (Q : Family (Query Model))
    (a b : Model) : Prop :=
  ∀ q, Q q → (q a ↔ q b)

def QueryInvariant {Model : Type u}
    (r : Model → Model → Prop)
    (q : Query Model) : Prop :=
  ∀ x y, r x y → (q x ↔ q y)

def FamilyInvariant {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model) : Prop :=
  ∀ x y, r x y → (H x ↔ H y)

theorem target_in_version {Model : Type u}
    (H : Family Model) (E : Family (Query Model)) (a : Model)
    (ha : H a) (hsound : SoundAt a E) :
    VersionSpace H E a := by
  exact ⟨ha, hsound⟩

theorem version_antitone_evidence {Model : Type u}
    (H : Family Model)
    (E F : Family (Query Model))
    (hEF : Subset E F) :
    Subset (VersionSpace H F) (VersionSpace H E) := by
  intro m hm
  exact ⟨hm.1, fun q hq => hm.2 q (hEF q hq)⟩

theorem version_monotone_hypotheses {Model : Type u}
    (H K : Family Model)
    (E : Family (Query Model))
    (hHK : Subset H K) :
    Subset (VersionSpace H E) (VersionSpace K E) := by
  intro m hm
  exact ⟨hHK m hm.1, hm.2⟩

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

/-- Sound evidence identifies the target iff it excludes every non-equivalent
competitor. The forward direction uses classical double-negation elimination. -/
theorem identifies_iff_hits_competitors {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (E : Family (Query Model)) :
    Identifies r H a E ↔
      H a ∧ SoundAt a E ∧ HitsCompetitors r H a E := by
  constructor
  · intro hid
    refine ⟨hid.1, hid.2.1, ?_⟩
    intro m hm hne
    exact Classical.byContradiction (fun hnone => by
      have hall : ∀ q, E q → q m := by
        intro q hq
        exact Classical.byContradiction (fun hqm =>
          hnone ⟨q, hq, hqm⟩)
      exact hne (hid.2.2 m ⟨hm, hall⟩))
  · intro h
    refine ⟨h.1, h.2.1, ?_⟩
    intro m hm
    exact Classical.byContradiction (fun hne => by
      have hw := h.2.2 m hm.1 hne
      cases hw with
      | intro q hq =>
          exact hq.2 (hm.2 q hq.1))

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
    have hhits :=
      (identifies_iff_hits_competitors r H a (FullEvidence Q a)).mp hid
    intro m hm hne
    have hw := hhits.2.2 m hm hne
    cases hw with
    | intro q hq =>
        exact ⟨q, hq.1.1, hq.1.2, hq.2⟩
  · intro hsep
    apply (identifies_iff_hits_competitors r H a (FullEvidence Q a)).mpr
    refine ⟨ha, ?_, ?_⟩
    · intro q hq
      exact hq.2
    · intro m hm hne
      have hw := hsep m hm hne
      cases hw with
      | intro q hq =>
          exact ⟨q, ⟨hq.1, hq.2.1⟩, hq.2.2⟩

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

def HoldsAll {Model : Type u} : List (Query Model) → Model → Prop
  | [], _ => True
  | q :: qs, m => q m ∧ HoldsAll qs m

def Conjunction {Model : Type u}
    (qs : List (Query Model)) : Query Model :=
  fun m => HoldsAll qs m

def ListIdentifies {Model : Type u}
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (qs : List (Query Model)) : Prop :=
  H a ∧ HoldsAll qs a ∧
    ∀ m, H m → HoldsAll qs m → r m a

def AllAdmissible {Model : Type u}
    (Q : Family (Query Model)) : List (Query Model) → Prop
  | [] => True
  | q :: qs => Q q ∧ AllAdmissible Q qs

def ClosedUnderFiniteConjunction {Model : Type u}
    (Q : Family (Query Model)) : Prop :=
  ∀ qs, AllAdmissible Q qs → Q (Conjunction qs)

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

/-! A finite discrimination example. The names stand for already-classified
isomorphism types; the proof concerns identification, not group axioms. -/

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
  have hf : carrierFour c8 :=
    h.2 carrierFour (Or.inr (Or.inr rfl))
  exact hf

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
        have hf : carrierFour c8 :=
          hm.2 carrierFour (Or.inr (Or.inr rfl))
        exact False.elim hf
    | d4 =>
        have hf : commutative d4 :=
          hm.2 commutative (Or.inr (Or.inl rfl))
        exact False.elim hf

end StructuralIdentification

#print axioms StructuralIdentification.identifies_iff_hits_competitors
#print axioms StructuralIdentification.observational_equivalence_blocks_identification
#print axioms StructuralIdentification.version_space_is_invariant
#print axioms StructuralIdentification.conjunction_collapse
#print axioms StructuralIdentification.three_truths_identify_c4
