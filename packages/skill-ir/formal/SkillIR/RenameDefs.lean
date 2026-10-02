import SkillIR.Core

/-! Renaming affects only the three structural identifier namespaces. -/
namespace SkillIR

structure Renaming where
  blockId : Nat → Nat
  instructionId : Nat → Nat
  resultId : Nat → Nat

def renameOperand (ρ : Renaming) : Operand → Operand
  | .result r => .result (ρ.resultId r)
  | .literal => .literal
  | .context key => .context key
  | .external resource => .external resource

def renameInstruction (ρ : Renaming) (i : Instruction) : Instruction :=
  { id := ρ.instructionId i.id, opcode := i.opcode,
    inputs := i.inputs.map (renameOperand ρ), outputs := i.outputs.map (renameOperand ρ) }

def renameBlock (ρ : Renaming) (b : Block) : Block :=
  { key := ρ.blockId b.key, id := ρ.blockId b.id, source := b.source,
    instructions := b.instructions.map (renameInstruction ρ) }

def renameEdge (ρ : Renaming) (e : Edge) : Edge :=
  { source := ρ.blockId e.source, target := ρ.blockId e.target, condition := e.condition }

def renameGraph (ρ : Renaming) (g : Graph) : Graph :=
  { entry := ρ.blockId g.entry, blocks := g.blocks.map (renameBlock ρ),
    edges := g.edges.map (renameEdge ρ), contexts := g.contexts }

theorem eq_iff_of_injective {α β : Type} {f : α → β}
    (hf : Function.Injective f) (a b : α) : f a = f b ↔ a = b :=
  ⟨fun h => hf h, congrArg f⟩

theorem mem_map_iff_of_injective {α β : Type} {f : α → β}
    (hf : Function.Injective f) (a : α) (xs : List α) :
    f a ∈ xs.map f ↔ a ∈ xs := by
  simp only [List.mem_map]
  constructor
  · rintro ⟨b, hb, heq⟩
    exact (hf heq) ▸ hb
  · intro h
    exact ⟨a, h, rfl⟩

theorem nodup_map_iff_of_injective {α β : Type} {f : α → β}
    (hf : Function.Injective f) (xs : List α) :
    (xs.map f).Nodup ↔ xs.Nodup := by
  induction xs with
  | nil => simp
  | cons x xs ih => simp [List.nodup_cons, mem_map_iff_of_injective hf, ih]

@[simp] theorem keys_rename (ρ : Renaming) (g : Graph) :
    (renameGraph ρ g).keys = g.keys.map ρ.blockId := by
  simp [Graph.keys, renameGraph, renameBlock, List.map_map, Function.comp_def]

@[simp] theorem blocks_length_rename (ρ : Renaming) (g : Graph) :
    (renameGraph ρ g).blocks.length = g.blocks.length := by
  simp [renameGraph]

end SkillIR
