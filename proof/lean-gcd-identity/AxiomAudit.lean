import PrimitiveTripleFilter

/-!
Candidate mechanical axiom audit. Unlike bare #print axioms, each #guard_msgs
command must match its expected info message or Lean rejects the file.
These expectations come from the author's report and await a pinned build.
-/

/-- info: 'primitive_composition_gcd_identity' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms primitive_composition_gcd_identity

/-- info: 'primitive_filter_criterion' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms primitive_filter_criterion
