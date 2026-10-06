import SkillIR.Core
import Lean.Data.Json

open Lean SkillIR

namespace SkillIR.JsonBoundary

def field (j : Json) (key : String) : Except String Json := j.getObjVal? key
def nat (j : Json) (key : String) : Except String Nat := do
  (← field j key).getNat?
def str (j : Json) (key : String) : Except String String := do
  (← field j key).getStr?
def list (j : Json) (key : String) (parse : Json → Except String α) : Except String (List α) := do
  let xs ← (← field j key).getArr?
  xs.toList.mapM parse

def operand (j : Json) : Except String Operand := do
  match ← str j "kind" with
  | "literal" => return .literal
  | "context" => return .context (← str j "id")
  | "external" => return .external (← str j "id")
  | "result" => return .result (← nat j "id")
  | s => throw s!"unknown operand kind: {s}"

def opcode (s : String) : Except String Opcode :=
  match s with
  | "business" => return .business
  | "dispatch" => return .dispatch
  | "return" => return .ret
  | _ => throw s!"unknown core opcode tag: {s}"

def source (s : String) : Except String Source :=
  match s with
  | "none" => return .none
  | "context" => return .context
  | "external" => return .external
  | _ => throw s!"unknown source tag: {s}"

def instruction (j : Json) : Except String Instruction := do
  return {
    id := ← nat j "id"
    opcode := ← opcode (← str j "opcode")
    inputs := ← list j "inputs" operand
    outputs := ← list j "outputs" operand }

def block (j : Json) : Except String Block := do
  return {
    key := ← nat j "key"
    id := ← nat j "id"
    source := ← source (← str j "source")
    instructions := ← list j "instructions" instruction }

def edge (j : Json) : Except String Edge := do
  let raw ← field j "condition"
  let condition ← if raw.isNull then pure none else some <$> raw.getStr?
  return { source := ← nat j "source", target := ← nat j "target", condition }

def graph (j : Json) : Except String Graph := do
  return {
    entry := ← nat j "entry"
    blocks := ← list j "blocks" block
    edges := ← list j "edges" edge
    contexts := ← list j "contexts" Json.getStr? }

def runLine (line : String) : Json :=
  match Json.parse line >>= graph with
  | .error message => Json.mkObj [("error", toJson message)]
  | .ok g => Json.mkObj [("accept", toJson (check g))]

end SkillIR.JsonBoundary

/-- JSONL interface: exactly one answer per nonempty input line. -/
def main : IO Unit := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    if !line.trimAscii.toString.isEmpty then
      stdout.putStrLn (SkillIR.JsonBoundary.runLine line).compress
      stdout.flush
