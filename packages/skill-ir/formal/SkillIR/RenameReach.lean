import SkillIR.RenameDefs

namespace SkillIR

theorem beq_iff_rename (ρ : Renaming) (hb : Function.Injective ρ.blockId) (a b : Nat) :
    (ρ.blockId a == ρ.blockId b) = (a == b) := by
  apply Bool.eq_iff_iff.mpr
  simp only [beq_iff_eq, hb.eq_iff]

/-- Every bounded closure round commutes with an injective block-ID rename. -/
theorem reachable_rename (ρ : Renaming) (g : Graph) (n a : Nat)
    (hb : Function.Injective ρ.blockId) :
    reachable (renameGraph ρ g) n (ρ.blockId a) = (reachable g n a).map ρ.blockId := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [reachable, ih, keys_rename]
    rw [← List.map_cons, List.filter_map]
    congr 1
    apply List.filter_congr
    intro b _
    simp [Function.comp_def, renameGraph, renameEdge, List.any_map,
      hb.eq_iff, beq_iff_rename ρ hb]

theorem reach_rename (ρ : Renaming) (g : Graph) (n a b : Nat)
    (hb : Function.Injective ρ.blockId) :
    Reach (renameGraph ρ g) n (ρ.blockId a) (ρ.blockId b) ↔ Reach g n a b := by
  simp only [Reach, reachable_rename ρ g n a hb, mem_map_iff_of_injective hb]

theorem root_rename (ρ : Renaming) (g : Graph) (r : Nat)
    (hb : Function.Injective ρ.blockId) :
    Root (renameGraph ρ g) (ρ.blockId r) ↔ Root g r := by
  simp [Root, renameGraph, renameEdge, hb.eq_iff]

end SkillIR
