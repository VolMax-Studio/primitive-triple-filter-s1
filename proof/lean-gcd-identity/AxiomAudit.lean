import PrimitiveTripleFilter

/-!
Mechanical axiom audit. Unlike bare #print axioms, each #guard_msgs command
must match its expected info message or Lean rejects the file.
-/

/-- info: 'primitive_composition_gcd_identity' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms primitive_composition_gcd_identity

/-- info: 'primitive_filter_criterion' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms primitive_filter_criterion
