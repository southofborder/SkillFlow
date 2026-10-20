import SkillIR

-- The command's output is retained by the differential-validation harness.
-- `sorryAx`, custom axioms, and kernel-bypassing tactics are not used.
#print axioms SkillIR.check_iff_wf
#print axioms SkillIR.check_sound
#print axioms SkillIR.check_complete
#print axioms SkillIR.wf_rename_iff
#print axioms SkillIR.check_rename
#print axioms SkillIR.Controlled.parse_print
#print axioms SkillIR.Controlled.recover_project
#print axioms SkillIR.Controlled.recover_parse_print_project
#print axioms SkillIR.Controlled.record_classification_location
#print axioms SkillIR.Controlled.constraint_scope_location
#print axioms SkillIR.Controlled.scoped_constraints_preserved
#print axioms SkillIR.Controlled.recorded_observation_preserved
#print axioms SkillIR.Controlled.links_sound
#print axioms SkillIR.Controlled.parseGraph_renderGraph
#print axioms SkillIR.Controlled.parseGraph_sound
#print axioms SkillIR.Controlled.renderGraph_injective
