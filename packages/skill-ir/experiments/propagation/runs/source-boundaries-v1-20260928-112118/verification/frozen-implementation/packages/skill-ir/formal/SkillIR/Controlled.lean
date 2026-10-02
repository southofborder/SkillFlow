import Std

/-! A lossless controlled-record language. Payload strings are opaque. The
    printer below is the single authority for the text consumed by the auditor. -/
namespace SkillIR.Controlled

inductive Term where
  | atom (value : String)
  | list (items : List Term)
  deriving Repr, BEq

inductive Token where
  | atom (value : String)
  | open
  | close
  deriving Repr, DecidableEq, BEq

def tokens : Term → List Token
  | .atom s => [.atom s]
  | .list xs => .open :: xs.flatMap tokens ++ [.close]

abbrev Stack := List (List Term)

def step : Token → Stack → Option Stack
  | .open, s => some ([] :: s)
  | .atom a, x :: s => some ((.atom a :: x) :: s)
  | .close, x :: y :: s => some ((.list x.reverse :: y) :: s)
  | _, _ => none

def runTokens : List Token → Stack → Option Stack
  | [], s => some s
  | t :: ts, s => (step t s).bind (runTokens ts)

theorem runTokens_append (a b : List Token) (s : Stack) :
    runTokens (a ++ b) s = (runTokens a s).bind (runTokens b) := by
  induction a generalizing s with
  | nil => rfl
  | cons h t ih =>
    simp only [List.cons_append, runTokens, Option.bind_assoc]
    cases step h s <;> simp_all

theorem runTokens_print (t : Term) :
    ∀ (acc : List Term) (s : Stack), runTokens (tokens t) (acc :: s) = some ((t :: acc) :: s) := by
  cases t with
  | atom v => intro acc s; simp [tokens, runTokens, step]
  | list xs =>
    have forest : ∀ (ys : List Term), (∀ t ∈ ys, ∀ acc s,
        runTokens (tokens t) (acc :: s) = some ((t :: acc) :: s)) →
        ∀ acc s, runTokens (ys.flatMap tokens) (acc :: s) = some ((ys.reverse ++ acc) :: s) := by
      intro ys
      induction ys with
      | nil => intro _ acc s; rfl
      | cons h t ht =>
        intro hy acc s
        rw [List.flatMap_cons, runTokens_append, hy h (by simp)]
        simp only [Option.bind_some]
        rw [ht (by intro z hz; exact hy z (by simp [hz]))]
        simp [List.reverse_cons, List.append_assoc]
    intro acc s
    simp only [tokens, List.cons_append, runTokens, step, Option.bind_some]
    rw [runTokens_append, forest xs (fun z hz => runTokens_print z)]
    simp [runTokens, step]
termination_by sizeOf t
decreasing_by
  have := List.sizeOf_lt_of_mem hz
  simp only [Term.list.sizeOf_spec]
  omega

def decodeTokens (ts : List Token) : Option Term := do
  match ← runTokens ts [[]] with
  | [[t]] => pure t
  | _ => none

theorem decodeTokens_tokens (t : Term) : decodeTokens (tokens t) = some t := by
  simp [decodeTokens, runTokens_print]

def escapeChar (c : Char) : List Char :=
  if c = '\\' then ['\\', '\\'] else if c = '"' then ['\\', '"']
  else if c = '\n' then ['\\', 'n'] else if c = '\r' then ['\\', 'r']
  else if c = '\t' then ['\\', 't'] else [c]

def unescapeChar (c : Char) : Char :=
  if c = 'n' then '\n' else if c = 'r' then '\r' else if c = 't' then '\t' else c

def escaped (s : List Char) : List Char := s.flatMap escapeChar

def readQuoted : List Char → Option (List Char × List Char)
  | [] => none
  | '"' :: rest => some ([], rest)
  | '\\' :: c :: rest => do
      let (value, remaining) ← readQuoted rest
      pure (unescapeChar c :: value, remaining)
  | '\\' :: [] => none
  | c :: rest => do
      let (value, remaining) ← readQuoted rest
      pure (c :: value, remaining)

theorem readQuoted_length (input value rest : List Char)
    (h : readQuoted input = some (value, rest)) : rest.length < input.length := by
  induction input using readQuoted.induct generalizing value rest with
  | case1 => simp [readQuoted] at h
  | case2 tail => simp [readQuoted] at h; obtain ⟨rfl, rfl⟩ := h; simp
  | case3 c tail ih =>
    simp only [readQuoted, Option.bind_eq_bind] at h
    cases hq : readQuoted tail with
    | none => simp [hq] at h
    | some p =>
      obtain ⟨v, r⟩ := p
      simp [hq] at h
      obtain ⟨rfl, rfl⟩ := h
      have := ih _ _ hq
      simp only [List.length_cons]
      omega
  | case4 => simp [readQuoted] at h
  | case5 c tail h₁ h₂ h₃ ih =>
    simp only [readQuoted] at h
    cases hq : readQuoted tail with
    | none => simp [hq] at h
    | some p =>
      obtain ⟨v, r⟩ := p
      simp [hq] at h
      obtain ⟨rfl, rfl⟩ := h
      have := ih _ _ hq
      simp only [List.length_cons]
      omega

theorem readQuoted_escaped (s rest : List Char) :
    readQuoted (escaped s ++ '"' :: rest) = some (s, rest) := by
  induction s with
  | nil => rfl
  | cons c cs ih =>
    simp only [escaped, List.flatMap_cons, List.append_assoc] at *
    by_cases h₁ : c = '\\'
    · subst c; simp [escapeChar, readQuoted, ih, unescapeChar]
    by_cases h₂ : c = '"'
    · subst c; simp [escapeChar, readQuoted, ih, unescapeChar]
    by_cases h₃ : c = '\n'
    · subst c; simp [escapeChar, readQuoted, ih, unescapeChar]
    by_cases h₄ : c = '\r'
    · subst c; simp [escapeChar, readQuoted, ih, unescapeChar]
    by_cases h₅ : c = '\t'
    · subst c; simp [escapeChar, readQuoted, ih, unescapeChar]
    simp [escapeChar, h₁, h₂, h₃, h₄, h₅, readQuoted, ih]

def lex (input : List Char) : Option (List Token) :=
  match input with
  | [] => some []
  | '[' :: rest => (Token.open :: ·) <$> lex rest
  | ']' :: rest => (Token.close :: ·) <$> lex rest
  | '\n' :: rest => lex rest
  | ' ' :: rest => lex rest
  | '"' :: rest =>
      match h : readQuoted rest with
      | none => none
      | some (value, remaining) => (Token.atom (String.ofList value) :: ·) <$> lex remaining
  | _ => none
termination_by input.length
decreasing_by
  all_goals simp_wf
  have := readQuoted_length rest value remaining h
  omega

def tokenChars : Token → List Char
  | .open => ['[', '\n']
  | .close => [']', '\n']
  | .atom s => '"' :: escaped s.toList ++ ['"', '\n']

theorem lex_print (ts : List Token) : lex (ts.flatMap tokenChars) = some ts := by
  induction ts with
  | nil => rw [List.flatMap_nil, lex]
  | cons t ts ih =>
    cases t with
    | «open» => simp [List.flatMap_cons, tokenChars, lex, ih]
    | close => simp [List.flatMap_cons, tokenChars, lex, ih]
    | atom s =>
      simp only [List.flatMap_cons, tokenChars, List.cons_append, List.append_assoc]
      rw [lex]
      rw [readQuoted_escaped]
      simp [lex, ih, String.ofList_toList]

theorem lex_spaces (n : Nat) (rest : List Char) :
    lex (List.replicate n ' ' ++ rest) = lex rest := by
  induction n with
  | zero => simp
  | succ n ih => simp [List.replicate_succ, lex, ih]

/-- Indented visible records. Formatting is included in the actual codec proof. -/
def prettyTokens : Nat → List Token → List Char
  | _, [] => []
  | depth, .open :: ts => '\n' :: (List.replicate (2 * depth) ' ' ++ '[' :: prettyTokens (depth + 1) ts)
  | depth, .close :: ts => ']' :: prettyTokens (depth - 1) ts
  | depth, .atom s :: ts => '"' :: (escaped s.toList ++ '"' :: ' ' :: prettyTokens depth ts)

theorem lex_prettyTokens (ts : List Token) (depth : Nat) :
    lex (prettyTokens depth ts) = some ts := by
  induction ts generalizing depth with
  | nil => rw [prettyTokens, lex]
  | cons t ts ih =>
    cases t with
    | «open» =>
      simp only [prettyTokens]
      rw [lex, lex_spaces, lex, ih]
      rfl
    | close => simp [prettyTokens, lex, ih]
    | atom s =>
      simp only [prettyTokens]
      rw [lex, readQuoted_escaped]
      simp [lex, ih, String.ofList_toList]

def printAt (depth : Nat) (t : Term) : String := String.ofList (prettyTokens depth (tokens t))

def print (t : Term) : String := printAt 0 t

def parse (s : String) : Option Term := (lex s.toList).bind decodeTokens

theorem parse_print (t : Term) : parse (print t) = some t := by
  simp [parse, print, printAt, String.toList_ofList, lex_prettyTokens, decodeTokens_tokens]

theorem parse_printAt (depth : Nat) (t : Term) : parse (printAt depth t) = some t := by
  simp [parse, printAt, String.toList_ofList, lex_prettyTokens, decodeTokens_tokens]

end SkillIR.Controlled
