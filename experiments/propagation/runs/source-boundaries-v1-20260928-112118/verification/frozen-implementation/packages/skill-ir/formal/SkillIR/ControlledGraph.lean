import SkillIR.Controlled

namespace SkillIR.Controlled

structure Operand where
  kind : String
  identifier : Option String
  semanticName : Option String
  literalJson : Option String
  deriving Repr, DecidableEq, BEq

structure Instruction where
  id : String
  opcode : String
  draft : Option String
  inputs : List Operand
  outputs : List Operand
  constraints : List String
  metadataJson : String
  deriving Repr, DecidableEq, BEq

structure Block where
  key : String
  id : String
  name : String
  source : Option String
  constraints : List String
  instructions : List Instruction
  deriving Repr, DecidableEq, BEq

structure Edge where
  source : String
  target : String
  condition : Option String
  deriving Repr, DecidableEq, BEq

/-- The rich, non-erasing input domain. Opaque JSON strings are supplied by the
    explicitly tested Python JSON boundary; their behavior is not interpreted. -/
structure RichGraph where
  entry : String
  contexts : List String
  constraints : List String
  blocks : List Block
  edges : List Edge
  deriving Repr, DecidableEq, BEq

inductive Scope where
  | graph | block (index : Nat) | instruction (blockIndex instructionIndex : Nat)
  deriving Repr, DecidableEq, BEq

def scopeName : Scope → String
  | .graph => "图级声明约束（声明不等于已实现）"
  | .block _ => "块级声明约束（声明不等于已实现）"
  | .instruction _ _ => "操作级声明约束（声明不等于已实现）"

def indexed (f : Nat → α → β) : Nat → List α → List β
  | _, [] => []
  | n, x :: xs => f n x :: indexed f (n + 1) xs

def many (f : α → Option β) : List α → Option (List β)
  | [] => some []
  | x :: xs => do
      let y ← f x
      let ys ← many f xs
      pure (y :: ys)

theorem many_indexed (f : Nat → α → β) (d : β → Option α)
    (h : ∀ n x, d (f n x) = some x) (n : Nat) (xs : List α) :
    many d (indexed f n xs) = some xs := by
  induction xs generalizing n with
  | nil => rfl
  | cons x xs ih => simp [indexed, many, h, ih]

def atom : Term → Option String
  | .atom s => some s
  | _ => none

def items : Term → Option (List Term)
  | .list xs => some xs
  | _ => none

def opt (s : Option String) : Term := match s with
  | none => .list [.atom "未记录"]
  | some x => .list [.atom "记录值", .atom x]

def unopt : Term → Option (Option String)
  | .list [.atom "未记录"] => some none
  | .list [.atom "记录值", .atom x] => some (some x)
  | _ => none

theorem unopt_opt (s : Option String) : unopt (opt s) = some s := by
  cases s <;> rfl

/-- Every visible record has a Chinese category, a public anchor and a location.
    The canonical parser also regenerates the entire text, so category/anchor
    edits cannot be accepted by merely decoding the slot values. -/
def atomicKind (kind : String) : Bool := kind ∈ [
  "声明入口块", "声明上下文键；声明不是读取操作",
  "图级声明约束（声明不等于已实现）", "块级声明约束（声明不等于已实现）",
  "操作级声明约束（声明不等于已实现）", "块字典键", "块ID", "块名称原文；仅作标签",
  "数据来源标记", "操作身份与开放操作名；记录顺序不保证执行成功",
  "操作数（种类与实际标识）", "metadata规范JSON；完整保留、未解释、未执行",
  "控制边；文字条件不求值", "结果引用绑定；仅按实际ID定位",
  "完整操作ID清单；按记录次序"]

def anchor (kind ref : String) : String :=
  if atomicKind kind then "fact:" ++ ref ++
    (if kind = "结果引用绑定；仅按实际ID定位" then ":link" else "") else ""

def record (kind ref : String) (xs : List Term) : Term :=
  .list (.atom kind :: .atom (anchor kind ref) :: .atom ref :: xs)

def unrecord : Term → Option (List Term)
  | .list (.atom _ :: .atom _ :: .atom _ :: xs) => some xs
  | _ => none

def field (kind ref value : String) : Term := record kind ref [.atom value]
def unfield (t : Term) : Option String := do
  match ← unrecord t with
  | [.atom s] => pure s
  | _ => none

theorem unfield_field (kind ref value : String) : unfield (field kind ref value) = some value := rfl

def strList (xs : List String) : Term := .list (xs.map .atom)
def unstrList (t : Term) : Option (List String) := do many atom (← items t)

theorem unstrList_strList (xs : List String) : unstrList (strList xs) = some xs := by
  have h : many atom (xs.map Term.atom) = some xs := by
    induction xs with
    | nil => rfl
    | cons x xs ih => simp [many, atom, ih]
  simpa [unstrList, strList, items] using h

def optionField (label ref : String) (value : Option String) : Term := record label ref [opt value]
def unoptionField (t : Term) : Option (Option String) := do
  match ← unrecord t with
  | [x] => unopt x
  | _ => none

theorem unoptionField_optionField (label ref : String) (value : Option String) :
    unoptionField (optionField label ref value) = some value := by
  simp [unoptionField, optionField, unrecord, record, unopt_opt]

def constraintsTerm (scope : Scope) (ref : String) (xs : List String) : Term :=
  record "约束列表" ref (indexed (fun n x => field (scopeName scope) (ref ++ "/" ++ toString n) x) 0 xs)

def unconstraints (t : Term) : Option (List String) := do many unfield (← unrecord t)

theorem unconstraints_constraints (scope : Scope) (ref : String) (xs : List String) :
    unconstraints (constraintsTerm scope ref xs) = some xs := by
  simp only [unconstraints, constraintsTerm, unrecord, record, Option.bind_some]
  exact many_indexed _ _ (by intro n x; rfl) _ _

def operandTerm (ref : String) (o : Operand) : Term := record "操作数（种类与实际标识）" ref [
  field "操作数种类" (ref ++ "/kind") o.kind,
  optionField "实际标识；不按语义标签合并" (ref ++ "/identifier") o.identifier,
  optionField "语义标签原文；仅作标签" (ref ++ "/semantic_name") o.semanticName,
  optionField "字面量规范JSON；未解释" (ref ++ "/literal_json") o.literalJson]

def unoperand (t : Term) : Option Operand := do
  match ← unrecord t with
  | [k, i, s, l] => return ⟨← unfield k, ← unoptionField i, ← unoptionField s, ← unoptionField l⟩
  | _ => none

theorem unoperand_operand (ref : String) (o : Operand) : unoperand (operandTerm ref o) = some o := by
  cases o
  simp [unoperand, operandTerm, unrecord, record, unfield_field, unoptionField_optionField]

def operandsTerm (label ref : String) (xs : List Operand) : Term :=
  record label ref (indexed (fun n x => operandTerm (ref ++ "/" ++ toString n) x) 0 xs)

def unoperands (t : Term) : Option (List Operand) := do many unoperand (← unrecord t)

theorem unoperands_operands (label ref : String) (xs : List Operand) :
    unoperands (operandsTerm label ref xs) = some xs := by
  simp only [unoperands, operandsTerm, unrecord, record, Option.bind_some]
  exact many_indexed _ _ (by intro n x; exact unoperand_operand _ _) _ _

def instructionTerm (bi ii : Nat) (ref : String) (i : Instruction) : Term := record "操作记录" ref [
  record "操作身份与开放操作名；记录顺序不保证执行成功" ref [
    field "指令ID" (ref ++ "/id") i.id,
    field "实际操作名；不补造其实现" (ref ++ "/opcode") i.opcode,
    optionField "草稿操作ID" (ref ++ "/draft") i.draft],
  operandsTerm "输入列表；按记录次序" (ref ++ "/inputs") i.inputs,
  operandsTerm "输出列表；按记录次序" (ref ++ "/outputs") i.outputs,
  constraintsTerm (.instruction bi ii) (ref ++ "/constraints") i.constraints,
  field "metadata规范JSON；完整保留、未解释、未执行" (ref ++ "/metadata_json") i.metadataJson]

def uninstruction (t : Term) : Option Instruction := do
  match ← unrecord t with
  | [header, ins, outs, cs, payload] =>
    match ← unrecord header with
    | [i, op, d] => return ⟨← unfield i, ← unfield op, ← unoptionField d,
        ← unoperands ins, ← unoperands outs, ← unconstraints cs, ← unfield payload⟩
    | _ => none
  | _ => none

theorem uninstruction_instruction (bi ii : Nat) (ref : String) (i : Instruction) :
    uninstruction (instructionTerm bi ii ref i) = some i := by
  cases i
  simp [uninstruction, instructionTerm, unrecord, record, unfield_field,
    unoptionField_optionField, unoperands_operands, unconstraints_constraints]

def blockTerm (bi : Nat) (b : Block) : Term :=
  let ref := "/blocks/" ++ toString bi
  record "块记录；名称不补造步骤" ref [
    field "块字典键" (ref ++ "/key") b.key,
    field "块ID" (ref ++ "/id") b.id,
    field "块名称原文；仅作标签" (ref ++ "/name") b.name,
    optionField "数据来源标记" (ref ++ "/source") b.source,
    constraintsTerm (.block bi) (ref ++ "/constraints") b.constraints,
    record "完整操作ID清单；按记录次序" (ref ++ "/instructions") [strList (b.instructions.map Instruction.id)],
    record "块内操作列表；严格保留记录次序" (ref ++ "/instructions")
      (indexed (fun ii i => instructionTerm bi ii (ref ++ "/instructions/" ++ toString ii) i) 0 b.instructions)]

def unblock (t : Term) : Option Block := do
  match ← unrecord t with
  | [k, i, n, s, cs, _inventory, ins] => return ⟨← unfield k, ← unfield i, ← unfield n,
      ← unoptionField s, ← unconstraints cs, ← many uninstruction (← unrecord ins)⟩
  | _ => none

theorem unblock_block (bi : Nat) (b : Block) : unblock (blockTerm bi b) = some b := by
  cases b
  simp [unblock, blockTerm, unrecord, record, unfield_field, unoptionField_optionField,
    unconstraints_constraints, many_indexed _ _ (fun n x => uninstruction_instruction _ _ _ _)]

def edgeTerm (ei : Nat) (e : Edge) : Term :=
  let ref := "/edges/" ++ toString ei
  record "控制边；文字条件不求值" ref [
    field "来源块" (ref ++ "/source") e.source,
    field "目标块" (ref ++ "/target") e.target,
    optionField "条件文字；未记录不等于恒真" (ref ++ "/condition") e.condition]

def unedge (t : Term) : Option Edge := do
  match ← unrecord t with
  | [s, t, c] => return ⟨← unfield s, ← unfield t, ← unoptionField c⟩
  | _ => none

theorem unedge_edge (ei : Nat) (e : Edge) : unedge (edgeTerm ei e) = some e := by
  cases e
  simp [unedge, edgeTerm, unrecord, record, unfield_field, unoptionField_optionField]

structure Occurrence where
  ref : String
  operand : Operand
  deriving Repr, DecidableEq, BEq

def occurrences (g : RichGraph) (output : Bool) : List Occurrence :=
  (indexed (fun bi b => (indexed (fun ii i =>
    let direction := if output then "/outputs/" else "/inputs/"
    indexed (fun oi o => ⟨"/blocks/" ++ toString bi ++ "/instructions/" ++ toString ii ++ direction ++ toString oi, o⟩)
      0 (if output then i.outputs else i.inputs)) 0 b.instructions).flatten) 0 g.blocks).flatten

structure Link where
  identifier : String
  useRef : String
  definitionRef : String
  deriving Repr, DecidableEq, BEq

def matchingLink (u d : Occurrence) : Option Link := do
  if u.operand.kind != "result" || d.operand.kind != "result" then none else
  match u.operand.identifier, d.operand.identifier with
  | some a, some b => if a = b then some ⟨a, u.ref, d.ref⟩ else none
  | _, _ => none

def links (g : RichGraph) : List Link :=
  (occurrences g false).flatMap (fun u => (occurrences g true).filterMap (matchingLink u))

theorem matchingLink_sound (u d : Occurrence) (l : Link) (h : matchingLink u d = some l) :
    u.operand.kind = "result" ∧ d.operand.kind = "result" ∧
    u.operand.identifier = some l.identifier ∧ d.operand.identifier = some l.identifier ∧
    l.useRef = u.ref ∧ l.definitionRef = d.ref := by
  unfold matchingLink at h
  split at h
  · contradiction
  · rename_i hkind
    simp at hkind
    split at h
    · rename_i a b ha hb
      split at h
      · rename_i hab
        simp only [Option.some.injEq] at h
        subst l
        exact ⟨hkind.1, hkind.2, ha, hab ▸ hb, rfl, rfl⟩
      · contradiction
    · contradiction

/-- Every displayed link comes from actual input/output occurrences carrying
    exactly the same result ID. Semantic labels have no role in this theorem. -/
theorem links_sound (g : RichGraph) (l : Link) (h : l ∈ links g) :
    ∃ u ∈ occurrences g false, ∃ d ∈ occurrences g true,
      u.operand.kind = "result" ∧ d.operand.kind = "result" ∧
      u.operand.identifier = some l.identifier ∧ d.operand.identifier = some l.identifier ∧
      l.useRef = u.ref ∧ l.definitionRef = d.ref := by
  simp only [links, List.mem_flatMap, List.mem_filterMap] at h
  obtain ⟨u, hu, d, hd, hm⟩ := h
  exact ⟨u, hu, d, hd, matchingLink_sound u d l hm⟩

def linkTerm (_n : Nat) (l : Link) : Term := record "结果引用绑定；仅按实际ID定位" l.useRef [
  field "结果ID" (l.useRef ++ "/identifier") l.identifier,
  field "使用位置" l.useRef l.useRef,
  field "定义位置" l.definitionRef l.definitionRef]

/-- FactDoc is the concrete tagged tree whose printed text is sent to the model.
    The explicit graph fields are visible records, not a hidden JSON sidecar. -/
abbrev FactDoc := Term

def project (g : RichGraph) : FactDoc := record "Skill-IR受控回述；只陈述图记录，不保证运行行为" "" [
  field "声明入口块" "/entry" g.entry,
  record "声明上下文键；声明不是读取操作" "/contexts" [strList g.contexts],
  constraintsTerm .graph "/constraints" g.constraints,
  record "块列表" "/blocks" (indexed blockTerm 0 g.blocks),
  record "控制边列表" "/edges" (indexed edgeTerm 0 g.edges),
  record "按实际标识展开的结果引用" "/links" (indexed linkTerm 0 (links g))]

def recover (t : FactDoc) : Option RichGraph := do
  match ← unrecord t with
  | [en, ctx, cs, bs, es, _ls] =>
    match ← unrecord ctx with
    | [keys] => return ⟨← unfield en, ← unstrList keys, ← unconstraints cs,
        ← many unblock (← unrecord bs), ← many unedge (← unrecord es)⟩
    | _ => none
  | _ => none

theorem recover_project (g : RichGraph) : recover (project g) = some g := by
  cases g
  simp [recover, project, unrecord, record, unfield_field, unstrList_strList,
    unconstraints_constraints, many_indexed blockTerm unblock unblock_block,
    many_indexed edgeTerm unedge unedge_edge]

/-- This theorem includes the actual escaped Unicode text codec. It is not a
    theorem merely about an unused intermediate graph representation. -/
theorem recover_parse_print_project (g : RichGraph) :
    (parse (print (project g))).bind recover = some g := by
  simp [parse_print, recover_project]

def recordHeader : Term → Option (String × String × String)
  | .list (.atom kind :: .atom id :: .atom ref :: _) => some (kind, id, ref)
  | _ => none

/-- Category, anchor, and location are actual serialized content. -/
theorem record_classification_location (kind ref : String) (xs : List Term) :
    (parse (print (record kind ref xs))).bind recordHeader =
      some (kind, anchor kind ref, ref) := by
  simp [parse_print, record, recordHeader]

theorem constraint_scope_location (scope : Scope) (ref : String) (value : String) :
    (parse (print (field (scopeName scope) ref value))).bind recordHeader =
      some (scopeName scope, anchor (scopeName scope) ref, ref) := by
  exact record_classification_location _ _ _

def constraintsAt (g : RichGraph) : Scope → Option (List String)
  | .graph => some g.constraints
  | .block bi => (g.blocks[bi]?).map Block.constraints
  | .instruction bi ii => do
      let b ← g.blocks[bi]?
      let i ← b.instructions[ii]?
      pure i.constraints

/-- Scope is a typed location in the graph, not a claim that a constraint runs. -/
theorem scoped_constraints_preserved (g : RichGraph) (scope : Scope) :
    ((parse (print (project g))).bind recover).bind (fun h => constraintsAt h scope) =
      constraintsAt g scope := by
  rw [recover_parse_print_project]
  rfl

/-- Consequently every observation of the complete rich record is preserved,
    including instruction/operand order, IDs, labels and opaque payload bytes. -/
theorem recorded_observation_preserved (g : RichGraph) (observe : RichGraph → α) :
    ((parse (print (project g))).bind recover).map observe = some (observe g) := by
  rw [recover_parse_print_project]
  rfl

structure Unit where
  id : String
  text : String
  kind : String
  ref : String
  deriving Repr

def unitsAt (depth : Nat) (t : Term) : List Unit :=
  match t with
  | .atom _ => []
  | .list xs =>
    match recordHeader t with
    | some (kind, id, ref) =>
      if atomicKind kind then [⟨id, printAt depth t, kind, ref⟩] else xs.flatMap (unitsAt (depth + 1))
    | none => xs.flatMap (unitsAt (depth + 1))

def units (t : Term) : List Unit := unitsAt 0 t

def renderGraph (g : RichGraph) : String := print (project g)

/-- Accept only the one canonical surface text, including all visible labels,
    anchors, scopes and derived reference links. No sidecar supplies graph data. -/
def parseGraph (text : String) : Option RichGraph := do
  let doc ← parse text
  let g ← recover doc
  if renderGraph g = text then some g else none

theorem parseGraph_renderGraph (g : RichGraph) : parseGraph (renderGraph g) = some g := by
  simp [parseGraph, renderGraph, parse_print, recover_project]

/-- An accepted document is the canonical visible record of the recovered
    graph, including every computed inventory, anchor, category and link. -/
theorem parseGraph_sound (text : String) (g : RichGraph) (h : parseGraph text = some g) :
    renderGraph g = text := by
  unfold parseGraph at h
  cases hp : parse text with
  | none => simp [hp] at h
  | some doc =>
    cases hr : recover doc with
    | none => simp [hp, hr] at h
    | some recovered =>
      by_cases he : renderGraph recovered = text
      · simp [hp, hr, he] at h
        subst g
        exact he
      · simp [hp, hr, he] at h

theorem renderGraph_injective : Function.Injective renderGraph := by
  intro a b h
  have := congrArg parseGraph h
  simpa only [parseGraph_renderGraph, Option.some.injEq] using this

end SkillIR.Controlled
