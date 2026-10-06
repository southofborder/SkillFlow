import Std

/-!
The normalized structural core. Strings carrying business meaning are opaque;
only block, instruction, and result identifiers are projected to natural numbers.
The Python boundary is responsible for field/schema validation and normalization.
No graph-rule answers or reachability tables enter this model.
-/
namespace SkillIR

inductive Opcode where
  | business | dispatch | ret
  deriving Repr, DecidableEq, BEq

inductive Source where
  | none | context | external
  deriving Repr, DecidableEq, BEq

inductive Operand where
  | literal
  | context (key : String)
  | external (resource : String)
  | result (id : Nat)
  deriving Repr, DecidableEq, BEq

structure Instruction where
  id : Nat
  opcode : Opcode
  inputs : List Operand
  outputs : List Operand
  deriving Repr, DecidableEq, BEq

structure Block where
  key : Nat
  id : Nat
  source : Source
  instructions : List Instruction
  deriving Repr, DecidableEq, BEq

structure Edge where
  source : Nat
  target : Nat
  condition : Option String
  deriving Repr, DecidableEq, BEq

structure Graph where
  entry : Nat
  blocks : List Block
  edges : List Edge
  contexts : List String
  deriving Repr, DecidableEq, BEq

def Operand.resultId : Operand → Option Nat
  | .result r => some r
  | _ => none

def Operand.IsResult : Operand → Prop
  | .result _ => True
  | _ => False

def Operand.IsContext : Operand → Prop
  | .context _ => True
  | _ => False

def Operand.IsExternalOrResult : Operand → Prop
  | .external _ | .result _ => True
  | _ => False

instance (o : Operand) : Decidable o.IsResult := by cases o <;> unfold Operand.IsResult <;> infer_instance
instance (o : Operand) : Decidable o.IsContext := by cases o <;> unfold Operand.IsContext <;> infer_instance
instance (o : Operand) : Decidable o.IsExternalOrResult := by cases o <;> unfold Operand.IsExternalOrResult <;> infer_instance

def Instruction.results (i : Instruction) : List Nat := i.outputs.filterMap Operand.resultId
def Block.results (b : Block) : List Nat := b.instructions.flatMap Instruction.results
def Graph.keys (g : Graph) : List Nat := g.blocks.map Block.key
def Graph.instructionIds (g : Graph) : List Nat :=
  g.blocks.flatMap (fun b => b.instructions.map Instruction.id)
def Graph.resultIds (g : Graph) : List Nat := g.blocks.flatMap Block.results
def Graph.definitions (g : Graph) : List (Nat × Nat) :=
  g.blocks.flatMap (fun b => b.results.map (fun r => (r, b.key)))

/-- Finite bounded closure. Every round retains previous nodes and follows one
    edge, restricted to the listed block keys (and the start itself). Conditions
    are opaque. The fixed candidate list bounds intermediate size linearly. -/
def reachable (g : Graph) : Nat → Nat → List Nat
  | 0, a => [a]
  | n + 1, a =>
    let previous := reachable g n a
    (a :: g.keys).filter (fun b => decide (b ∈ previous) ||
      g.edges.any (fun e => decide (e.source ∈ previous) && e.target == b))

/-- Membership in the explicit `fuel`-round closure, not a checker result.
    `WF` uses `blocks.length` rounds on graphs whose endpoints exist. -/
def Reach (g : Graph) (fuel a b : Nat) : Prop := b ∈ reachable g fuel a
instance (g : Graph) (n a b : Nat) : Decidable (Reach g n a b) := by
  unfold Reach; infer_instance

theorem reach_zero_iff (g : Graph) (a b : Nat) : Reach g 0 a b ↔ b = a := by
  simp [Reach, reachable]

/-- Logical characterization of one closure round, independent of `check`. -/
theorem reach_succ_iff (g : Graph) (n a b : Nat) :
    Reach g (n + 1) a b ↔
    (b = a ∨ b ∈ g.keys) ∧
    (Reach g n a b ∨ ∃ e ∈ g.edges, Reach g n a e.source ∧ e.target = b) := by
  simp [Reach, reachable, List.any_eq_true]

/-- The named entry and every block without predecessors are roots. -/
def Root (g : Graph) (r : Nat) : Prop :=
  r = g.entry ∨ ∀ e ∈ g.edges, e.target ≠ r
instance (g : Graph) (r : Nat) : Decidable (Root g r) := by unfold Root; infer_instance

/-- Last instruction is a terminator; earlier instructions are business ops. -/
def TerminalShape : List Instruction → Prop
  | [] => False
  | [i] => i.opcode = .dispatch ∨ i.opcode = .ret
  | i :: j :: rest => i.opcode = .business ∧ TerminalShape (j :: rest)
def decTerminalShape : (xs : List Instruction) → Decidable (TerminalShape xs)
  | [] => inferInstanceAs (Decidable False)
  | [i] => inferInstanceAs (Decidable (i.opcode = .dispatch ∨ i.opcode = .ret))
  | i :: j :: rest => by
    haveI := decTerminalShape (j :: rest)
    unfold TerminalShape; infer_instance
instance (xs : List Instruction) : Decidable (TerminalShape xs) := decTerminalShape xs

/-- A local result use must follow an earlier definition, even in a loop. -/
def LocalOrder (allDefs seen : List Nat) : List Instruction → Prop
  | [] => True
  | i :: rest =>
      (∀ r ∈ i.inputs.filterMap Operand.resultId, r ∈ allDefs → r ∈ seen) ∧
      LocalOrder allDefs (seen ++ i.results) rest
def decLocalOrder (allDefs seen : List Nat) : (xs : List Instruction) → Decidable (LocalOrder allDefs seen xs)
  | [] => inferInstanceAs (Decidable True)
  | i :: rest => by
    haveI := decLocalOrder allDefs (seen ++ i.results) rest
    unfold LocalOrder; infer_instance
instance (allDefs seen : List Nat) (xs : List Instruction) : Decidable (LocalOrder allDefs seen xs) := decLocalOrder allDefs seen xs

def RawOperand (g : Graph) (source : Source) (first : Bool) : Operand → Prop
  | .context key => source = .context ∧ first = true ∧ key ∈ g.contexts
  | _ => True
instance (g : Graph) (s : Source) (first : Bool) (o : Operand) : Decidable (RawOperand g s first o) := by
  cases o <;> unfold RawOperand <;> infer_instance

def RawInputs (g : Graph) (s : Source) (first : Bool) : List Instruction → Prop
  | [] => True
  | i :: rest => (∀ o ∈ i.inputs, RawOperand g s first o) ∧ RawInputs g s false rest
def decRawInputs (g : Graph) (s : Source) (first : Bool) : (xs : List Instruction) → Decidable (RawInputs g s first xs)
  | [] => inferInstanceAs (Decidable True)
  | i :: rest => by
    haveI := decRawInputs g s false rest
    unfold RawInputs; infer_instance
instance (g : Graph) (s : Source) (first : Bool) (xs : List Instruction) : Decidable (RawInputs g s first xs) := decRawInputs g s first xs

/-- Source blocks contain one acquisition followed by one terminator. -/
def SourceShape (b : Block) : Prop :=
  match b.source with
  | .none => True
  | .context => match b.instructions with
    | [a, _] => a.outputs ≠ [] ∧ a.inputs ≠ [] ∧ ∀ o ∈ a.inputs, o.IsContext
    | _ => False
  | .external => match b.instructions with
    | [a, _] => a.outputs ≠ [] ∧ a.opcode = .business ∧ ∃ o ∈ a.inputs, o.IsExternalOrResult
    | _ => False
instance (b : Block) : Decidable (SourceShape b) := by
  unfold SourceShape
  split
  · infer_instance
  · split <;> infer_instance
  · split <;> infer_instance

def OutputsWF (i : Instruction) : Prop :=
  (∀ o ∈ i.outputs, o.IsResult) ∧
  (i.opcode ≠ .business → i.outputs = [])
instance (i : Instruction) : Decidable (OutputsWF i) := by unfold OutputsWF; infer_instance

def Outgoing (g : Graph) (b : Block) : List Edge := g.edges.filter (fun e => e.source == b.key)

def ExitWF (g : Graph) (b : Block) : Prop :=
  match b.instructions.getLast? with
  | none => False
  | some i =>
    (i.opcode = .ret → Outgoing g b = []) ∧
    (i.opcode = .dispatch → Outgoing g b ≠ [] ∧
      ((Outgoing g b).length > 1 ∨ (∃ e ∈ Outgoing g b, e.condition ≠ none) → i.inputs ≠ []))
instance (g : Graph) (b : Block) : Decidable (ExitWF g b) := by
  unfold ExitWF; split <;> infer_instance

def BlockWF (g : Graph) (b : Block) : Prop :=
  b.key = b.id ∧ TerminalShape b.instructions ∧ SourceShape b ∧
  (∀ i ∈ b.instructions, OutputsWF i) ∧
  RawInputs g b.source true b.instructions ∧
  LocalOrder b.results [] b.instructions ∧ ExitWF g b
instance (g : Graph) (b : Block) : Decidable (BlockWF g b) := by unfold BlockWF; infer_instance

def ResultUse (g : Graph) (reader : Nat) : Operand → Prop
  | .result r => ∃ d ∈ g.definitions, d.1 = r ∧
      (d.2 = reader ∨ Reach g g.blocks.length d.2 reader)
  | _ => True
instance (g : Graph) (reader : Nat) (o : Operand) : Decidable (ResultUse g reader o) := by
  cases o <;> unfold ResultUse <;> infer_instance

/-- Declarative well-formedness of the normalized structural core.
    It asserts only written structure/reference connectivity (may paths).
    It does not establish condition feasibility or must-availability. -/
def WF (g : Graph) : Prop :=
  g.keys.Nodup ∧ g.instructionIds.Nodup ∧ g.resultIds.Nodup ∧ g.contexts.Nodup ∧
  g.entry ∈ g.keys ∧ g.edges.Nodup ∧
  (∀ e ∈ g.edges, e.source ∈ g.keys ∧ e.target ∈ g.keys) ∧
  (∀ b ∈ g.blocks, BlockWF g b) ∧
  (∀ b ∈ g.blocks, ∃ r ∈ g.keys, Root g r ∧ Reach g g.blocks.length r b.key) ∧
  (∀ b ∈ g.blocks, ∀ i ∈ b.instructions, ∀ o ∈ i.inputs, ResultUse g b.key o)

instance (g : Graph) : Decidable (WF g) := by unfold WF; infer_instance

/-- Executable reflection of the finite declarative proposition. -/
def check (g : Graph) : Bool := decide (WF g)

theorem check_iff_wf (g : Graph) : check g = true ↔ WF g :=
  ⟨of_decide_eq_true, decide_eq_true⟩

theorem check_sound (g : Graph) (h : check g = true) : WF g :=
  (check_iff_wf g).mp h

theorem check_complete (g : Graph) (h : WF g) : check g = true :=
  (check_iff_wf g).mpr h

end SkillIR
