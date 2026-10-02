import SkillIR.ControlledGraph
import Lean.Data.Json

open Lean SkillIR.Controlled

/-! JSON is an explicitly unproved I/O boundary. The mathematical printer and
    parser used here are the exact functions in the audited round-trip theorem. -/
namespace SkillIR.Controlled.JsonBoundary

def field (j : Json) (key : String) : Except String Json := j.getObjVal? key
def str (j : Json) (key : String) : Except String String := do (← field j key).getStr?
def nullable (j : Json) (key : String) : Except String (Option String) := do
  let v ← field j key
  if v.isNull then pure none else some <$> v.getStr?
def list (j : Json) (key : String) (parse : Json → Except String α) : Except String (List α) := do
  let xs ← (← field j key).getArr?
  xs.toList.mapM parse

def operand (j : Json) : Except String Operand := do
  return ⟨← str j "kind", ← nullable j "identifier", ← nullable j "semantic_name", ← nullable j "literal_json"⟩

def instruction (j : Json) : Except String Instruction := do
  return ⟨← str j "id", ← str j "opcode", ← nullable j "draft", ← list j "inputs" operand,
    ← list j "outputs" operand, ← list j "constraints" Json.getStr?, ← str j "metadata_json"⟩

def block (j : Json) : Except String Block := do
  return ⟨← str j "key", ← str j "id", ← str j "name", ← nullable j "source",
    ← list j "constraints" Json.getStr?, ← list j "instructions" instruction⟩

def edge (j : Json) : Except String Edge := do
  return ⟨← str j "source", ← str j "target", ← nullable j "condition"⟩

def graph (j : Json) : Except String RichGraph := do
  return ⟨← str j "entry", ← list j "contexts" Json.getStr?, ← list j "constraints" Json.getStr?,
    ← list j "blocks" block, ← list j "edges" edge⟩

def operandJson (o : Operand) : Json := Json.mkObj [
  ("kind", toJson o.kind), ("identifier", toJson o.identifier),
  ("semantic_name", toJson o.semanticName), ("literal_json", toJson o.literalJson)]

def instructionJson (i : Instruction) : Json := Json.mkObj [
  ("id", toJson i.id), ("opcode", toJson i.opcode), ("draft", toJson i.draft),
  ("inputs", toJson (i.inputs.map operandJson)), ("outputs", toJson (i.outputs.map operandJson)),
  ("constraints", toJson i.constraints), ("metadata_json", toJson i.metadataJson)]

def blockJson (b : Block) : Json := Json.mkObj [
  ("key", toJson b.key), ("id", toJson b.id), ("name", toJson b.name), ("source", toJson b.source),
  ("constraints", toJson b.constraints), ("instructions", toJson (b.instructions.map instructionJson))]

def edgeJson (e : Edge) : Json := Json.mkObj [
  ("source", toJson e.source), ("target", toJson e.target), ("condition", toJson e.condition)]

def graphJson (g : RichGraph) : Json := Json.mkObj [
  ("entry", toJson g.entry), ("contexts", toJson g.contexts), ("constraints", toJson g.constraints),
  ("blocks", toJson (g.blocks.map blockJson)), ("edges", toJson (g.edges.map edgeJson))]

def unitJson (u : Unit) : Json := Json.mkObj [
  ("id", toJson u.id), ("text", toJson u.text), ("kind", toJson u.kind), ("ref", toJson u.ref)]

def linkJson (l : Link) : Json := Json.mkObj [
  ("identifier", toJson l.identifier), ("use_ref", toJson l.useRef), ("definition_ref", toJson l.definitionRef)]

def answer (g : RichGraph) (text : String) : Json := Json.mkObj [
  ("ok", toJson true), ("protocol", toJson "skill-ir-controlled-v1"), ("text", toJson text),
  ("recovered_graph", graphJson g), ("units", toJson ((units (project g)).map unitJson)),
  ("links", toJson ((links g).map linkJson))]

def errorJson (message : String) : Json := Json.mkObj [("ok", toJson false), ("error", toJson message)]

def runRequest (j : Json) : Except String Json := do
  let command ← str j "command"
  if command = "render" then
    let g ← graph (← field j "graph")
    let text := renderGraph g
    match parseGraph text with
    | none => throw "internal controlled-text round-trip failure"
    | some recovered =>
      if recovered = g then pure (answer recovered text)
      else throw "internal rich-record round-trip mismatch"
  else if command = "parse" then
    let text ← str j "text"
    match parseGraph text with
    | none => throw "invalid or noncanonical controlled text (including category, location or link mismatch)"
    | some recovered => pure (answer recovered text)
  else throw "command must be render or parse"

def runLine (line : String) : Json :=
  match Json.parse line >>= runRequest with
  | .error message => errorJson message
  | .ok result => result

end SkillIR.Controlled.JsonBoundary

def main : IO _root_.Unit := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    if !line.trimAscii.toString.isEmpty then
      stdout.putStrLn (SkillIR.Controlled.JsonBoundary.runLine line).compress
      stdout.flush
