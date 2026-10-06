import SkillIR.RenameReach

namespace SkillIR

theorem exists_mem_map_iff {α β : Type} (f : α → β) (xs : List α) (P : β → Prop) :
    (∃ y ∈ xs.map f, P y) ↔ ∃ x ∈ xs, P (f x) := by
  constructor
  · rintro ⟨y, hy, hp⟩
    obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hy
    exact ⟨x, hx, hp⟩
  · rintro ⟨x, hx, hp⟩
    exact ⟨f x, List.mem_map.mpr ⟨x, hx, rfl⟩, hp⟩

@[simp] theorem isResult_rename (ρ : Renaming) (o : Operand) :
    (renameOperand ρ o).IsResult ↔ o.IsResult := by
  cases o <;> simp [renameOperand, Operand.IsResult]

@[simp] theorem isContext_rename (ρ : Renaming) (o : Operand) :
    (renameOperand ρ o).IsContext ↔ o.IsContext := by
  cases o <;> simp [renameOperand, Operand.IsContext]

@[simp] theorem isExternalOrResult_rename (ρ : Renaming) (o : Operand) :
    (renameOperand ρ o).IsExternalOrResult ↔ o.IsExternalOrResult := by
  cases o <;> simp [renameOperand, Operand.IsExternalOrResult]

theorem operand_results_rename (ρ : Renaming) (xs : List Operand) :
    (xs.map (renameOperand ρ)).filterMap Operand.resultId =
      (xs.filterMap Operand.resultId).map ρ.resultId := by
  induction xs with
  | nil => rfl
  | cons x xs ih => cases x <;> simp [renameOperand, Operand.resultId, List.filterMap_cons, ih]

@[simp] theorem instruction_results_rename (ρ : Renaming) (i : Instruction) :
    (renameInstruction ρ i).results = i.results.map ρ.resultId := by
  exact operand_results_rename ρ i.outputs

@[simp] theorem block_results_rename (ρ : Renaming) (b : Block) :
    (renameBlock ρ b).results = b.results.map ρ.resultId := by
  simp [Block.results, renameBlock, List.flatMap_map, List.map_flatMap]

@[simp] theorem graph_instructionIds_rename (ρ : Renaming) (g : Graph) :
    (renameGraph ρ g).instructionIds = g.instructionIds.map ρ.instructionId := by
  simp [Graph.instructionIds, renameGraph, renameBlock, renameInstruction,
    List.flatMap_map, List.map_flatMap, List.map_map, Function.comp_def]

@[simp] theorem graph_resultIds_rename (ρ : Renaming) (g : Graph) :
    (renameGraph ρ g).resultIds = g.resultIds.map ρ.resultId := by
  simp [Graph.resultIds, renameGraph, List.flatMap_map, List.map_flatMap]

@[simp] theorem graph_definitions_rename (ρ : Renaming) (g : Graph) :
    (renameGraph ρ g).definitions =
      g.definitions.map (fun d => (ρ.resultId d.1, ρ.blockId d.2)) := by
  simp only [Graph.definitions, renameGraph, List.flatMap_map, Function.comp_def,
    block_results_rename, List.map_flatMap, List.map_map]
  rfl

theorem terminalShape_rename (ρ : Renaming) (xs : List Instruction) :
    TerminalShape (xs.map (renameInstruction ρ)) ↔ TerminalShape xs := by
  induction xs with
  | nil => rfl
  | cons i xs ih =>
    cases xs with
    | nil => rfl
    | cons j rest =>
      change (i.opcode = .business ∧ TerminalShape ((j :: rest).map (renameInstruction ρ))) ↔
        (i.opcode = .business ∧ TerminalShape (j :: rest))
      exact and_congr Iff.rfl ih

theorem outputsWF_rename (ρ : Renaming) (i : Instruction) :
    OutputsWF (renameInstruction ρ i) ↔ OutputsWF i := by
  simp [OutputsWF, renameInstruction]

theorem rawOperand_rename (ρ : Renaming) (g : Graph) (s : Source) (first : Bool)
    (o : Operand) :
    RawOperand (renameGraph ρ g) s first (renameOperand ρ o) ↔ RawOperand g s first o := by
  cases o <;> simp [renameOperand, RawOperand, renameGraph]

theorem rawInputs_rename (ρ : Renaming) (g : Graph) (s : Source) (first : Bool)
    (xs : List Instruction) :
    RawInputs (renameGraph ρ g) s first (xs.map (renameInstruction ρ)) ↔
      RawInputs g s first xs := by
  induction xs generalizing first with
  | nil => rfl
  | cons i xs ih =>
    simp [RawInputs, renameInstruction, rawOperand_rename, ih]

theorem localOrder_rename (ρ : Renaming) (hr : Function.Injective ρ.resultId)
    (allDefs seen : List Nat) (xs : List Instruction) :
    LocalOrder (allDefs.map ρ.resultId) (seen.map ρ.resultId)
      (xs.map (renameInstruction ρ)) ↔ LocalOrder allDefs seen xs := by
  induction xs generalizing seen with
  | nil => rfl
  | cons i xs ih =>
    simp only [List.map_cons, LocalOrder]
    change ((∀ r ∈ (i.inputs.map (renameOperand ρ)).filterMap Operand.resultId,
      r ∈ allDefs.map ρ.resultId → r ∈ seen.map ρ.resultId) ∧
      LocalOrder (allDefs.map ρ.resultId)
        (seen.map ρ.resultId ++ (renameInstruction ρ i).results)
        (xs.map (renameInstruction ρ))) ↔ _
    rw [operand_results_rename, instruction_results_rename, ← List.map_append, ih]
    simp only [List.forall_mem_map, mem_map_iff_of_injective hr]

theorem sourceShape_rename (ρ : Renaming) (b : Block) :
    SourceShape (renameBlock ρ b) ↔ SourceShape b := by
  cases b with
  | mk key id source xs =>
    cases xs with
    | nil => cases source <;> simp [SourceShape, renameBlock]
    | cons a xs =>
      cases xs with
      | nil => cases source <;> simp [SourceShape, renameBlock]
      | cons z xs =>
        cases xs <;> cases source <;>
          simp only [SourceShape, renameBlock, renameInstruction, List.map_cons,
            List.map_nil, ne_eq, List.map_eq_nil_iff, List.forall_mem_map,
            exists_mem_map_iff, isContext_rename, isExternalOrResult_rename]

theorem renameEdge_injective (ρ : Renaming) (hb : Function.Injective ρ.blockId) :
    Function.Injective (renameEdge ρ) := by
  intro a b h
  cases a with
  | mk sa ta ca =>
    cases b with
    | mk sb tb cb =>
      simp only [renameEdge, Edge.mk.injEq] at h
      rcases h with ⟨hs, ht, hc⟩
      simp [hb hs, hb ht, hc]

theorem outgoing_rename (ρ : Renaming) (hb : Function.Injective ρ.blockId)
    (g : Graph) (b : Block) :
    Outgoing (renameGraph ρ g) (renameBlock ρ b) = (Outgoing g b).map (renameEdge ρ) := by
  simp [Outgoing, renameGraph, renameBlock, List.filter_map, Function.comp_def,
    renameEdge, beq_iff_rename ρ hb]

theorem exitWF_rename (ρ : Renaming) (hb : Function.Injective ρ.blockId)
    (g : Graph) (b : Block) :
    ExitWF (renameGraph ρ g) (renameBlock ρ b) ↔ ExitWF g b := by
  unfold ExitWF
  simp only [renameBlock, List.getLast?_map]
  cases h : b.instructions.getLast? with
  | none => simp
  | some i =>
    simp only [Option.map_some]
    change ((_ → Outgoing (renameGraph ρ g) (renameBlock ρ b) = []) ∧
      (_ → Outgoing (renameGraph ρ g) (renameBlock ρ b) ≠ [] ∧
        ((Outgoing (renameGraph ρ g) (renameBlock ρ b)).length > 1 ∨
          (∃ e ∈ Outgoing (renameGraph ρ g) (renameBlock ρ b), e.condition ≠ none) →
          (renameInstruction ρ i).inputs ≠ []))) ↔ _
    rw [outgoing_rename ρ hb]
    simp only [renameInstruction, ne_eq, List.map_eq_nil_iff, List.length_map,
      exists_mem_map_iff, renameEdge]

theorem blockWF_rename (ρ : Renaming) (hb : Function.Injective ρ.blockId)
    (hr : Function.Injective ρ.resultId) (g : Graph) (b : Block) :
    BlockWF (renameGraph ρ g) (renameBlock ρ b) ↔ BlockWF g b := by
  unfold BlockWF
  rw [sourceShape_rename, exitWF_rename ρ hb, block_results_rename]
  simp only [renameBlock]
  rw [eq_iff_of_injective hb, terminalShape_rename]
  simp only [List.forall_mem_map, outputsWF_rename]
  rw [rawInputs_rename]
  have order := localOrder_rename ρ hr b.results [] b.instructions
  simpa using and_congr Iff.rfl (and_congr Iff.rfl (and_congr Iff.rfl
    (and_congr Iff.rfl (and_congr Iff.rfl (and_congr order Iff.rfl)))))

theorem resultUse_rename (ρ : Renaming) (hb : Function.Injective ρ.blockId)
    (hr : Function.Injective ρ.resultId) (g : Graph) (reader : Nat) (o : Operand) :
    ResultUse (renameGraph ρ g) (ρ.blockId reader) (renameOperand ρ o) ↔
      ResultUse g reader o := by
  cases o with
  | literal => rfl
  | context key => rfl
  | external resource => rfl
  | result r =>
    simp only [renameOperand, ResultUse, graph_definitions_rename, exists_mem_map_iff,
      blocks_length_rename, eq_iff_of_injective hr, eq_iff_of_injective hb,
      reach_rename ρ g _ _ _ hb]

/-- Injective renaming preserves and reflects all normalized structural rules.
    A bijection on each namespace is a special case. Context keys, opcodes,
    source categories, conditions, ordering, and all graph incidence stay fixed. -/
theorem wf_rename_iff (ρ : Renaming) (g : Graph)
    (hb : Function.Injective ρ.blockId) (hi : Function.Injective ρ.instructionId)
    (hr : Function.Injective ρ.resultId) : WF (renameGraph ρ g) ↔ WF g := by
  simp only [WF, keys_rename, graph_instructionIds_rename, graph_resultIds_rename]
  simp only [show (renameGraph ρ g).contexts = g.contexts from rfl,
    show (renameGraph ρ g).entry = ρ.blockId g.entry from rfl,
    show (renameGraph ρ g).edges = g.edges.map (renameEdge ρ) from rfl,
    show (renameGraph ρ g).blocks = g.blocks.map (renameBlock ρ) from rfl,
    List.length_map, nodup_map_iff_of_injective hb, nodup_map_iff_of_injective hi,
    nodup_map_iff_of_injective hr, nodup_map_iff_of_injective (renameEdge_injective ρ hb),
    List.forall_mem_map, exists_mem_map_iff, blockWF_rename ρ hb hr,
    mem_map_iff_of_injective hb]
  simp only [renameEdge, renameBlock, renameInstruction, List.forall_mem_map,
    mem_map_iff_of_injective hb, root_rename ρ g _ hb,
    reach_rename ρ g _ _ _ hb, resultUse_rename ρ hb hr]

theorem check_rename (ρ : Renaming) (g : Graph)
    (hb : Function.Injective ρ.blockId) (hi : Function.Injective ρ.instructionId)
    (hr : Function.Injective ρ.resultId) : check (renameGraph ρ g) = check g := by
  apply Bool.eq_iff_iff.mpr
  rw [check_iff_wf, check_iff_wf, wf_rename_iff ρ g hb hi hr]

end SkillIR
