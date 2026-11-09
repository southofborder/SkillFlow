These fixtures copy the closed backend-r3 010 and 013 runs' frozen source, selected
CFG, sealed Task, accepted processing/sensitivity, and the exact failed second
correspondence candidate. Their provenance records the original paths and byte
hashes. The failed references are intentionally preserved: 010 R4/R6 use an output
slot instead of the expression's operation/self target; 013 R3 uses an expression
body path instead of a normalized expression target.

Offline tests make explicit substitutions in copies using the program-generated
reference view, then use normal fragment assembly, annotation compilation,
propagation and forward constraint checks. Production does not rewrite bad
references. These are new offline tests, not saved-run replay or changed online
evidence, and they do not execute the source Skill or invoke a model.

Reference acceptance is separate from semantic completeness. The unchanged 010
abstract control checker still reports possible violating paths for R4/R6. The
unchanged 013 append/output gaps still prevent complete propagation and leave R3
unestablished. Neither limitation is converted into a passing DOE conclusion.
