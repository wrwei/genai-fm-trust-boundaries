theory AMR_Artifacts
  imports AMR_Extraction
begin
text \<open>Generated concrete definitions; byte identities and frontend dependencies are in snapshot.json. No parser correctness claim.\<close>
definition probe_envs :: "(nat \<Rightarrow> bool) list" where
 "probe_envs=[(\<lambda>a. if a=0 then False else if a=1 then False else if a=2 then False else False),(\<lambda>a. if a=0 then False else if a=1 then False else if a=2 then True else False),(\<lambda>a. if a=0 then False else if a=1 then True else if a=2 then False else False),(\<lambda>a. if a=0 then False else if a=1 then True else if a=2 then True else False),(\<lambda>a. if a=0 then True else if a=1 then False else if a=2 then False else False),(\<lambda>a. if a=0 then True else if a=1 then False else if a=2 then True else False),(\<lambda>a. if a=0 then True else if a=1 then True else if a=2 then False else False),(\<lambda>a. if a=0 then True else if a=1 then True else if a=2 then True else False)]"
text \<open>Raw SHA256 8c9a614d51b0004e5b3b039666c31232bc15e72ce6045a9cda6684ff52ce7824\<close>
definition p_8c9a614d51b0_select_source :: "(expr \<times> (nat \<times> nat option)) list" where
 "p_8c9a614d51b0_select_source=[((BAnd [(Atom 0),(Atom 1)]),(0,None)),((BAnd [(Atom 0),(Atom 2)]),(1,None)),((Lit True),(2,None))]"
definition p_8c9a614d51b0_select_target :: "(insn list \<times> (nat \<times> nat option)) list" where
 "p_8c9a614d51b0_select_target=[([Load 0,Load 1,Conj 2],(0,None)),([Load 0,Load 2,Conj 2,Load 0,Load 1,Conj 2,Neg,Conj 2],(1,None)),([Push True,Load 0,Load 1,Conj 2,Neg,Conj 2,Load 0,Load 2,Conj 2,Neg,Conj 2],(2,None))]"
lemma p_8c9a614d51b0_select_binding: "extract_rules p_8c9a614d51b0_select_source=p_8c9a614d51b0_select_target"
 by code_simp
corollary p_8c9a614d51b0_select_preserves:
 "target_results env p_8c9a614d51b0_select_target=result_list (source_result env p_8c9a614d51b0_select_source)"
 by (simp only:p_8c9a614d51b0_select_binding[symmetric] extraction_preserves)
definition p_8c9a614d51b0_step_source :: "(expr \<times> (nat \<times> nat option)) list" where
 "p_8c9a614d51b0_step_source=[((BAnd [(BOr [(BNot (Atom 5)),(BNot (Atom 12)),(Atom 6)]),(Atom 10)]),(5,Some 4)),((BOr [(BNot (Atom 5)),(BNot (Atom 12)),(Atom 6)]),(5,Some 3)),((BAnd [(Atom 5),(Atom 12),(BNot (Atom 6)),(Atom 11),(Atom 8),(Atom 10)]),(8,Some 6)),((BAnd [(Atom 5),(Atom 12),(BNot (Atom 6)),(Atom 11),(Atom 8)]),(5,Some 3)),((BAnd [(Atom 5),(Atom 12),(BNot (Atom 6)),(BNot (BAnd [(Atom 11),(Atom 8)])),(Atom 7),(Atom 9)]),(7,Some 2)),((BAnd [(Atom 16),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(BNot (Atom 7)),(BNot (Atom 8))]),(3,Some 1)),((Atom 17),(6,Some 5)),((Lit True),(4,Some 2))]"
definition p_8c9a614d51b0_step_target :: "(insn list \<times> (nat \<times> nat option)) list" where
 "p_8c9a614d51b0_step_target=[([Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2],(5,Some 4)),([Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2],(5,Some 3)),([Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Load 10,Conj 6,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Neg,Conj 2],(8,Some 6)),([Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 5,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Load 10,Conj 6,Neg,Conj 2],(5,Some 3)),([Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 2,Neg,Load 7,Load 9,Conj 6,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Load 10,Conj 6,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 5,Neg,Conj 2],(7,Some 2)),([Load 16,Load 10,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Load 10,Conj 6,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 5,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 2,Neg,Load 7,Load 9,Conj 6,Neg,Conj 2],(5,Some 3)),([Load 7,Neg,Load 8,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Load 10,Conj 6,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 5,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 2,Neg,Load 7,Load 9,Conj 6,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2],(3,Some 1)),([Load 17,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Load 10,Conj 6,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 5,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 2,Neg,Load 7,Load 9,Conj 6,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2,Load 7,Neg,Load 8,Neg,Conj 2,Neg,Conj 2],(6,Some 5)),([Push True,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Load 10,Conj 6,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 5,Neg,Conj 2,Load 5,Load 12,Load 6,Neg,Load 11,Load 8,Conj 2,Neg,Load 7,Load 9,Conj 6,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2,Load 7,Neg,Load 8,Neg,Conj 2,Neg,Conj 2,Load 17,Neg,Conj 2],(4,Some 2))]"
lemma p_8c9a614d51b0_step_binding: "extract_rules p_8c9a614d51b0_step_source=p_8c9a614d51b0_step_target"
 by code_simp
corollary p_8c9a614d51b0_step_preserves:
 "target_results env p_8c9a614d51b0_step_target=result_list (source_result env p_8c9a614d51b0_step_source)"
 by (simp only:p_8c9a614d51b0_step_binding[symmetric] extraction_preserves)
text \<open>Raw SHA256 c7e96f0c096ea4b1cb67607f700b23f24a34d6d11d3f0c36b7acba6bb446e8b9\<close>
definition p_c7e96f0c096e_select_source :: "(expr \<times> (nat \<times> nat option)) list" where
 "p_c7e96f0c096e_select_source=[((BAnd [(Atom 0),(Atom 1)]),(0,None)),((BAnd [(Atom 0),(Atom 2)]),(1,None)),((Lit True),(2,None))]"
definition p_c7e96f0c096e_select_target :: "(insn list \<times> (nat \<times> nat option)) list" where
 "p_c7e96f0c096e_select_target=[([Load 0,Load 1,Conj 2],(0,None)),([Load 0,Load 2,Conj 2,Load 0,Load 1,Conj 2,Neg,Conj 2],(1,None)),([Push True,Load 0,Load 1,Conj 2,Neg,Conj 2,Load 0,Load 2,Conj 2,Neg,Conj 2],(2,None))]"
lemma p_c7e96f0c096e_select_binding: "extract_rules p_c7e96f0c096e_select_source=p_c7e96f0c096e_select_target"
 by code_simp
corollary p_c7e96f0c096e_select_preserves:
 "target_results env p_c7e96f0c096e_select_target=result_list (source_result env p_c7e96f0c096e_select_source)"
 by (simp only:p_c7e96f0c096e_select_binding[symmetric] extraction_preserves)
definition p_c7e96f0c096e_step_source :: "(expr \<times> (nat \<times> nat option)) list" where
 "p_c7e96f0c096e_step_source=[((BAnd [(BOr [(BNot (Atom 5)),(BNot (Atom 12)),(Atom 6)]),(Atom 10)]),(5,Some 4)),((BAnd [(BOr [(BNot (Atom 5)),(BNot (Atom 12)),(Atom 6)]),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(Atom 11),(Atom 8),(Atom 10)]),(8,Some 6)),((BAnd [(Atom 11),(Atom 8),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(Atom 7),(Atom 9)]),(7,Some 2)),((BAnd [(Atom 16),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(BNot (Atom 7)),(BNot (Atom 8))]),(3,Some 1)),((Atom 17),(6,Some 5)),((Lit True),(4,Some 2))]"
definition p_c7e96f0c096e_step_target :: "(insn list \<times> (nat \<times> nat option)) list" where
 "p_c7e96f0c096e_step_target=[([Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2],(5,Some 4)),([Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2],(5,Some 3)),([Load 11,Load 8,Load 10,Conj 3,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2],(8,Some 6)),([Load 11,Load 8,Load 10,Neg,Conj 3,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2],(5,Some 3)),([Load 7,Load 9,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2],(7,Some 2)),([Load 16,Load 10,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2],(5,Some 3)),([Load 7,Neg,Load 8,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2],(3,Some 1)),([Load 17,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2,Load 7,Neg,Load 8,Neg,Conj 2,Neg,Conj 2],(6,Some 5)),([Push True,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2,Load 7,Neg,Load 8,Neg,Conj 2,Neg,Conj 2,Load 17,Neg,Conj 2],(4,Some 2))]"
lemma p_c7e96f0c096e_step_binding: "extract_rules p_c7e96f0c096e_step_source=p_c7e96f0c096e_step_target"
 by code_simp
corollary p_c7e96f0c096e_step_preserves:
 "target_results env p_c7e96f0c096e_step_target=result_list (source_result env p_c7e96f0c096e_step_source)"
 by (simp only:p_c7e96f0c096e_step_binding[symmetric] extraction_preserves)
text \<open>Raw SHA256 9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd\<close>
definition p_9eaa530b5825_select_source :: "(expr \<times> (nat \<times> nat option)) list" where
 "p_9eaa530b5825_select_source=[((BNot (Atom 0)),(2,None)),((BAnd [(Atom 1),(BNot (Atom 2))]),(0,None)),((BAnd [(Atom 2),(BNot (Atom 1))]),(1,None)),((BAnd [(Atom 1),(Atom 2),(Atom 3),(BNot (Atom 4))]),(0,None)),((BAnd [(Atom 1),(Atom 2),(Atom 4),(BNot (Atom 3))]),(1,None)),((BAnd [(Atom 1),(Atom 2)]),(0,None)),((Lit True),(2,None))]"
definition p_9eaa530b5825_select_target :: "(insn list \<times> (nat \<times> nat option)) list" where
 "p_9eaa530b5825_select_target=[([Load 0,Neg],(2,None)),([Load 1,Load 2,Neg,Conj 2,Load 0,Neg,Neg,Conj 2],(0,None)),([Load 2,Load 1,Neg,Conj 2,Load 0,Neg,Neg,Conj 2,Load 1,Load 2,Neg,Conj 2,Neg,Conj 2],(1,None)),([Load 1,Load 2,Load 3,Load 4,Neg,Conj 4,Load 0,Neg,Neg,Conj 2,Load 1,Load 2,Neg,Conj 2,Neg,Conj 2,Load 2,Load 1,Neg,Conj 2,Neg,Conj 2],(0,None)),([Load 1,Load 2,Load 4,Load 3,Neg,Conj 4,Load 0,Neg,Neg,Conj 2,Load 1,Load 2,Neg,Conj 2,Neg,Conj 2,Load 2,Load 1,Neg,Conj 2,Neg,Conj 2,Load 1,Load 2,Load 3,Load 4,Neg,Conj 4,Neg,Conj 2],(1,None)),([Load 1,Load 2,Conj 2,Load 0,Neg,Neg,Conj 2,Load 1,Load 2,Neg,Conj 2,Neg,Conj 2,Load 2,Load 1,Neg,Conj 2,Neg,Conj 2,Load 1,Load 2,Load 3,Load 4,Neg,Conj 4,Neg,Conj 2,Load 1,Load 2,Load 4,Load 3,Neg,Conj 4,Neg,Conj 2],(0,None)),([Push True,Load 0,Neg,Neg,Conj 2,Load 1,Load 2,Neg,Conj 2,Neg,Conj 2,Load 2,Load 1,Neg,Conj 2,Neg,Conj 2,Load 1,Load 2,Load 3,Load 4,Neg,Conj 4,Neg,Conj 2,Load 1,Load 2,Load 4,Load 3,Neg,Conj 4,Neg,Conj 2,Load 1,Load 2,Conj 2,Neg,Conj 2],(2,None))]"
lemma p_9eaa530b5825_select_binding: "extract_rules p_9eaa530b5825_select_source=p_9eaa530b5825_select_target"
 by code_simp
corollary p_9eaa530b5825_select_preserves:
 "target_results env p_9eaa530b5825_select_target=result_list (source_result env p_9eaa530b5825_select_source)"
 by (simp only:p_9eaa530b5825_select_binding[symmetric] extraction_preserves)
definition p_9eaa530b5825_step_source :: "(expr \<times> (nat \<times> nat option)) list" where
 "p_9eaa530b5825_step_source=[((BAnd [(Atom 10),(BOr [(BNot (Atom 5)),(BNot (Atom 12)),(Atom 6)])]),(5,Some 4)),((BAnd [(BNot (Atom 10)),(BOr [(BNot (Atom 5)),(BNot (Atom 12)),(Atom 6)])]),(5,Some 3)),((BAnd [(Atom 11),(Atom 8),(Atom 10)]),(8,Some 6)),((BAnd [(Atom 11),(Atom 8),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(Atom 7),(Atom 9)]),(7,Some 2)),((BAnd [(Atom 16),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(BNot (Atom 7)),(BNot (Atom 8))]),(3,Some 1)),((Atom 17),(6,Some 5)),((Lit True),(4,Some 2))]"
definition p_9eaa530b5825_step_target :: "(insn list \<times> (nat \<times> nat option)) list" where
 "p_9eaa530b5825_step_target=[([Load 10,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2],(5,Some 4)),([Load 10,Neg,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Load 10,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2],(5,Some 3)),([Load 11,Load 8,Load 10,Conj 3,Load 10,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 10,Neg,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2],(8,Some 6)),([Load 11,Load 8,Load 10,Neg,Conj 3,Load 10,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 10,Neg,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2],(5,Some 3)),([Load 7,Load 9,Conj 2,Load 10,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 10,Neg,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2],(7,Some 2)),([Load 16,Load 10,Neg,Conj 2,Load 10,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 10,Neg,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2],(5,Some 3)),([Load 7,Neg,Load 8,Neg,Conj 2,Load 10,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 10,Neg,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2],(3,Some 1)),([Load 17,Load 10,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 10,Neg,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2,Load 7,Neg,Load 8,Neg,Conj 2,Neg,Conj 2],(6,Some 5)),([Push True,Load 10,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 10,Neg,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2,Load 7,Neg,Load 8,Neg,Conj 2,Neg,Conj 2,Load 17,Neg,Conj 2],(4,Some 2))]"
lemma p_9eaa530b5825_step_binding: "extract_rules p_9eaa530b5825_step_source=p_9eaa530b5825_step_target"
 by code_simp
corollary p_9eaa530b5825_step_preserves:
 "target_results env p_9eaa530b5825_step_target=result_list (source_result env p_9eaa530b5825_step_source)"
 by (simp only:p_9eaa530b5825_step_binding[symmetric] extraction_preserves)
text \<open>Raw SHA256 eb5a9d7915a64a816b95223e864e47f9fcff117b490c78994b6fdb61285d6ed3\<close>
definition p_eb5a9d7915a6_select_source :: "(expr \<times> (nat \<times> nat option)) list" where
 "p_eb5a9d7915a6_select_source=[((BAnd [(Atom 0),(Atom 1),(BNot (Atom 2))]),(0,None)),((BAnd [(Atom 0),(Atom 2),(BNot (Atom 1))]),(1,None)),((BAnd [(Atom 0),(Atom 1),(Atom 2)]),(0,None)),((Lit True),(2,None))]"
definition p_eb5a9d7915a6_select_target :: "(insn list \<times> (nat \<times> nat option)) list" where
 "p_eb5a9d7915a6_select_target=[([Load 0,Load 1,Load 2,Neg,Conj 3],(0,None)),([Load 0,Load 2,Load 1,Neg,Conj 3,Load 0,Load 1,Load 2,Neg,Conj 3,Neg,Conj 2],(1,None)),([Load 0,Load 1,Load 2,Conj 3,Load 0,Load 1,Load 2,Neg,Conj 3,Neg,Conj 2,Load 0,Load 2,Load 1,Neg,Conj 3,Neg,Conj 2],(0,None)),([Push True,Load 0,Load 1,Load 2,Neg,Conj 3,Neg,Conj 2,Load 0,Load 2,Load 1,Neg,Conj 3,Neg,Conj 2,Load 0,Load 1,Load 2,Conj 3,Neg,Conj 2],(2,None))]"
lemma p_eb5a9d7915a6_select_binding: "extract_rules p_eb5a9d7915a6_select_source=p_eb5a9d7915a6_select_target"
 by code_simp
corollary p_eb5a9d7915a6_select_preserves:
 "target_results env p_eb5a9d7915a6_select_target=result_list (source_result env p_eb5a9d7915a6_select_source)"
 by (simp only:p_eb5a9d7915a6_select_binding[symmetric] extraction_preserves)
definition p_eb5a9d7915a6_step_source :: "(expr \<times> (nat \<times> nat option)) list" where
 "p_eb5a9d7915a6_step_source=[((BAnd [(BOr [(BNot (Atom 5)),(BNot (Atom 12)),(Atom 6)]),(Atom 10)]),(5,Some 4)),((BAnd [(BOr [(BNot (Atom 5)),(BNot (Atom 12)),(Atom 6)]),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(Atom 11),(Atom 8),(Atom 10)]),(8,Some 6)),((BAnd [(Atom 11),(Atom 8),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(Atom 7),(Atom 9)]),(7,Some 2)),((BAnd [(Atom 16),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(BNot (Atom 7)),(BNot (Atom 8))]),(3,Some 1)),((Atom 17),(6,Some 5)),((Lit True),(4,Some 2))]"
definition p_eb5a9d7915a6_step_target :: "(insn list \<times> (nat \<times> nat option)) list" where
 "p_eb5a9d7915a6_step_target=[([Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2],(5,Some 4)),([Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2],(5,Some 3)),([Load 11,Load 8,Load 10,Conj 3,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2],(8,Some 6)),([Load 11,Load 8,Load 10,Neg,Conj 3,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2],(5,Some 3)),([Load 7,Load 9,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2],(7,Some 2)),([Load 16,Load 10,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2],(5,Some 3)),([Load 7,Neg,Load 8,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2],(3,Some 1)),([Load 17,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2,Load 7,Neg,Load 8,Neg,Conj 2,Neg,Conj 2],(6,Some 5)),([Push True,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2,Load 7,Neg,Load 8,Neg,Conj 2,Neg,Conj 2,Load 17,Neg,Conj 2],(4,Some 2))]"
lemma p_eb5a9d7915a6_step_binding: "extract_rules p_eb5a9d7915a6_step_source=p_eb5a9d7915a6_step_target"
 by code_simp
corollary p_eb5a9d7915a6_step_preserves:
 "target_results env p_eb5a9d7915a6_step_target=result_list (source_result env p_eb5a9d7915a6_step_source)"
 by (simp only:p_eb5a9d7915a6_step_binding[symmetric] extraction_preserves)
text \<open>Raw SHA256 d864df79a77d78db50ad14bf6f683ec2897dfa0c2668f95244fda76c6f7f8c75\<close>
definition p_d864df79a77d_select_source :: "(expr \<times> (nat \<times> nat option)) list" where
 "p_d864df79a77d_select_source=[((BAnd [(Atom 0),(Atom 1)]),(0,None)),((BAnd [(Atom 0),(Atom 2)]),(1,None)),((Lit True),(2,None))]"
definition p_d864df79a77d_select_target :: "(insn list \<times> (nat \<times> nat option)) list" where
 "p_d864df79a77d_select_target=[([Load 0,Load 1,Conj 2],(0,None)),([Load 0,Load 2,Conj 2,Load 0,Load 1,Conj 2,Neg,Conj 2],(1,None)),([Push True,Load 0,Load 1,Conj 2,Neg,Conj 2,Load 0,Load 2,Conj 2,Neg,Conj 2],(2,None))]"
lemma p_d864df79a77d_select_binding: "extract_rules p_d864df79a77d_select_source=p_d864df79a77d_select_target"
 by code_simp
corollary p_d864df79a77d_select_preserves:
 "target_results env p_d864df79a77d_select_target=result_list (source_result env p_d864df79a77d_select_source)"
 by (simp only:p_d864df79a77d_select_binding[symmetric] extraction_preserves)
definition p_d864df79a77d_step_source :: "(expr \<times> (nat \<times> nat option)) list" where
 "p_d864df79a77d_step_source=[((BAnd [(BOr [(BNot (Atom 5)),(BNot (Atom 12)),(Atom 6)]),(Atom 10)]),(5,Some 4)),((BAnd [(BOr [(BNot (Atom 5)),(BNot (Atom 12)),(Atom 6)]),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(Atom 11),(Atom 8),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(Atom 11),(Atom 8),(Atom 10)]),(8,Some 6)),((BAnd [(Atom 7),(Atom 9)]),(7,Some 2)),((BAnd [(Atom 16),(BNot (Atom 10))]),(5,Some 3)),((BAnd [(BNot (Atom 7)),(BNot (Atom 8))]),(3,Some 1)),((Atom 17),(6,Some 5)),((Lit True),(4,Some 2))]"
definition p_d864df79a77d_step_target :: "(insn list \<times> (nat \<times> nat option)) list" where
 "p_d864df79a77d_step_target=[([Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2],(5,Some 4)),([Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2],(5,Some 3)),([Load 11,Load 8,Load 10,Neg,Conj 3,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2],(5,Some 3)),([Load 11,Load 8,Load 10,Conj 3,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2],(8,Some 6)),([Load 7,Load 9,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2],(7,Some 2)),([Load 16,Load 10,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2],(5,Some 3)),([Load 7,Neg,Load 8,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2],(3,Some 1)),([Load 17,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2,Load 7,Neg,Load 8,Neg,Conj 2,Neg,Conj 2],(6,Some 5)),([Push True,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Conj 2,Neg,Conj 2,Load 5,Neg,Load 12,Neg,Load 6,Disj 3,Load 10,Neg,Conj 2,Neg,Conj 2,Load 11,Load 8,Load 10,Neg,Conj 3,Neg,Conj 2,Load 11,Load 8,Load 10,Conj 3,Neg,Conj 2,Load 7,Load 9,Conj 2,Neg,Conj 2,Load 16,Load 10,Neg,Conj 2,Neg,Conj 2,Load 7,Neg,Load 8,Neg,Conj 2,Neg,Conj 2,Load 17,Neg,Conj 2],(4,Some 2))]"
lemma p_d864df79a77d_step_binding: "extract_rules p_d864df79a77d_step_source=p_d864df79a77d_step_target"
 by code_simp
corollary p_d864df79a77d_step_preserves:
 "target_results env p_d864df79a77d_step_target=result_list (source_result env p_d864df79a77d_step_source)"
 by (simp only:p_d864df79a77d_step_binding[symmetric] extraction_preserves)
lemma expr_true: "compile (Lit True)=[Push True]"
 by code_simp
lemma expr_true_source_values:
 "map (\<lambda>env. eval_expr env (Lit True)) probe_envs=[True,True,True,True,True,True,True,True]"
 by code_simp
lemma expr_true_target_values:
 "map (\<lambda>env. run_code [Push True] env []) probe_envs=[Some [True],Some [True],Some [True],Some [True],Some [True],Some [True],Some [True],Some [True]]"
 by code_simp
lemma expr_false: "compile (Lit False)=[Push False]"
 by code_simp
lemma expr_false_source_values:
 "map (\<lambda>env. eval_expr env (Lit False)) probe_envs=[False,False,False,False,False,False,False,False]"
 by code_simp
lemma expr_false_target_values:
 "map (\<lambda>env. run_code [Push False] env []) probe_envs=[Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [False]]"
 by code_simp
lemma expr_atom: "compile (Atom 0)=[Load 0]"
 by code_simp
lemma expr_atom_source_values:
 "map (\<lambda>env. eval_expr env (Atom 0)) probe_envs=[False,False,False,False,True,True,True,True]"
 by code_simp
lemma expr_atom_target_values:
 "map (\<lambda>env. run_code [Load 0] env []) probe_envs=[Some [False],Some [False],Some [False],Some [False],Some [True],Some [True],Some [True],Some [True]]"
 by code_simp
lemma expr_not_atom: "compile (BNot (Atom 0))=[Load 0,Neg]"
 by code_simp
lemma expr_not_atom_source_values:
 "map (\<lambda>env. eval_expr env (BNot (Atom 0))) probe_envs=[True,True,True,True,False,False,False,False]"
 by code_simp
lemma expr_not_atom_target_values:
 "map (\<lambda>env. run_code [Load 0,Neg] env []) probe_envs=[Some [True],Some [True],Some [True],Some [True],Some [False],Some [False],Some [False],Some [False]]"
 by code_simp
lemma expr_double_not: "compile (BNot (BNot (Atom 0)))=[Load 0]"
 by code_simp
lemma expr_double_not_source_values:
 "map (\<lambda>env. eval_expr env (BNot (BNot (Atom 0)))) probe_envs=[False,False,False,False,True,True,True,True]"
 by code_simp
lemma expr_double_not_target_values:
 "map (\<lambda>env. run_code [Load 0] env []) probe_envs=[Some [False],Some [False],Some [False],Some [False],Some [True],Some [True],Some [True],Some [True]]"
 by code_simp
lemma expr_triple_not: "compile (BNot (BNot (BNot (Atom 0))))=[Load 0,Neg]"
 by code_simp
lemma expr_triple_not_source_values:
 "map (\<lambda>env. eval_expr env (BNot (BNot (BNot (Atom 0))))) probe_envs=[True,True,True,True,False,False,False,False]"
 by code_simp
lemma expr_triple_not_target_values:
 "map (\<lambda>env. run_code [Load 0,Neg] env []) probe_envs=[Some [True],Some [True],Some [True],Some [True],Some [False],Some [False],Some [False],Some [False]]"
 by code_simp
lemma expr_not_true: "compile (BNot (Lit True))=[Push True,Neg]"
 by code_simp
lemma expr_not_true_source_values:
 "map (\<lambda>env. eval_expr env (BNot (Lit True))) probe_envs=[False,False,False,False,False,False,False,False]"
 by code_simp
lemma expr_not_true_target_values:
 "map (\<lambda>env. run_code [Push True,Neg] env []) probe_envs=[Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [False]]"
 by code_simp
lemma expr_and_two: "compile (BAnd [(Atom 0),(Atom 1)])=[Load 0,Load 1,Conj 2]"
 by code_simp
lemma expr_and_two_source_values:
 "map (\<lambda>env. eval_expr env (BAnd [(Atom 0),(Atom 1)])) probe_envs=[False,False,False,False,False,False,True,True]"
 by code_simp
lemma expr_and_two_target_values:
 "map (\<lambda>env. run_code [Load 0,Load 1,Conj 2] env []) probe_envs=[Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [True],Some [True]]"
 by code_simp
lemma expr_or_three: "compile (BOr [(Atom 0),(Atom 1),(Atom 2)])=[Load 0,Load 1,Load 2,Disj 3]"
 by code_simp
lemma expr_or_three_source_values:
 "map (\<lambda>env. eval_expr env (BOr [(Atom 0),(Atom 1),(Atom 2)])) probe_envs=[False,True,True,True,True,True,True,True]"
 by code_simp
lemma expr_or_three_target_values:
 "map (\<lambda>env. run_code [Load 0,Load 1,Load 2,Disj 3] env []) probe_envs=[Some [False],Some [True],Some [True],Some [True],Some [True],Some [True],Some [True],Some [True]]"
 by code_simp
lemma expr_and_three: "compile (BAnd [(Atom 0),(Atom 1),(Atom 2)])=[Load 0,Load 1,Load 2,Conj 3]"
 by code_simp
lemma expr_and_three_source_values:
 "map (\<lambda>env. eval_expr env (BAnd [(Atom 0),(Atom 1),(Atom 2)])) probe_envs=[False,False,False,False,False,False,False,True]"
 by code_simp
lemma expr_and_three_target_values:
 "map (\<lambda>env. run_code [Load 0,Load 1,Load 2,Conj 3] env []) probe_envs=[Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [True]]"
 by code_simp
lemma expr_nested: "compile (BAnd [(BOr [(Atom 0),(BNot (Atom 1))]),(BNot (BAnd [(Atom 1),(Atom 2)]))])=[Load 0,Load 1,Neg,Disj 2,Load 1,Load 2,Conj 2,Neg,Conj 2]"
 by code_simp
lemma expr_nested_source_values:
 "map (\<lambda>env. eval_expr env (BAnd [(BOr [(Atom 0),(BNot (Atom 1))]),(BNot (BAnd [(Atom 1),(Atom 2)]))])) probe_envs=[True,True,False,False,True,True,True,False]"
 by code_simp
lemma expr_nested_target_values:
 "map (\<lambda>env. run_code [Load 0,Load 1,Neg,Disj 2,Load 1,Load 2,Conj 2,Neg,Conj 2] env []) probe_envs=[Some [True],Some [True],Some [False],Some [False],Some [True],Some [True],Some [True],Some [False]]"
 by code_simp
lemma expr_repeated: "compile (BOr [(Atom 0),(Atom 0),(BNot (Atom 0))])=[Load 0,Load 0,Load 0,Neg,Disj 3]"
 by code_simp
lemma expr_repeated_source_values:
 "map (\<lambda>env. eval_expr env (BOr [(Atom 0),(Atom 0),(BNot (Atom 0))])) probe_envs=[True,True,True,True,True,True,True,True]"
 by code_simp
lemma expr_repeated_target_values:
 "map (\<lambda>env. run_code [Load 0,Load 0,Load 0,Neg,Disj 3] env []) probe_envs=[Some [True],Some [True],Some [True],Some [True],Some [True],Some [True],Some [True],Some [True]]"
 by code_simp
lemma expr_seven_nots: "compile (BNot (BNot (BNot (BNot (BNot (BNot (BNot (Atom 0))))))))=[Load 0,Neg]"
 by code_simp
lemma expr_seven_nots_source_values:
 "map (\<lambda>env. eval_expr env (BNot (BNot (BNot (BNot (BNot (BNot (BNot (Atom 0))))))))) probe_envs=[True,True,True,True,False,False,False,False]"
 by code_simp
lemma expr_seven_nots_target_values:
 "map (\<lambda>env. run_code [Load 0,Neg] env []) probe_envs=[Some [True],Some [True],Some [True],Some [True],Some [False],Some [False],Some [False],Some [False]]"
 by code_simp
lemma expr_empty_and: "compile (BAnd [])=[Conj 0]"
 by code_simp
lemma expr_empty_and_source_values:
 "map (\<lambda>env. eval_expr env (BAnd [])) probe_envs=[True,True,True,True,True,True,True,True]"
 by code_simp
lemma expr_empty_and_target_values:
 "map (\<lambda>env. run_code [Conj 0] env []) probe_envs=[Some [True],Some [True],Some [True],Some [True],Some [True],Some [True],Some [True],Some [True]]"
 by code_simp
lemma expr_empty_or: "compile (BOr [])=[Disj 0]"
 by code_simp
lemma expr_empty_or_source_values:
 "map (\<lambda>env. eval_expr env (BOr [])) probe_envs=[False,False,False,False,False,False,False,False]"
 by code_simp
lemma expr_empty_or_target_values:
 "map (\<lambda>env. run_code [Disj 0] env []) probe_envs=[Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [False]]"
 by code_simp
lemma expr_unary_and: "compile (BAnd [(Atom 0)])=[Load 0,Conj 1]"
 by code_simp
lemma expr_unary_and_source_values:
 "map (\<lambda>env. eval_expr env (BAnd [(Atom 0)])) probe_envs=[False,False,False,False,True,True,True,True]"
 by code_simp
lemma expr_unary_and_target_values:
 "map (\<lambda>env. run_code [Load 0,Conj 1] env []) probe_envs=[Some [False],Some [False],Some [False],Some [False],Some [True],Some [True],Some [True],Some [True]]"
 by code_simp
lemma expr_unary_or: "compile (BOr [(Atom 0)])=[Load 0,Disj 1]"
 by code_simp
lemma expr_unary_or_source_values:
 "map (\<lambda>env. eval_expr env (BOr [(Atom 0)])) probe_envs=[False,False,False,False,True,True,True,True]"
 by code_simp
lemma expr_unary_or_target_values:
 "map (\<lambda>env. run_code [Load 0,Disj 1] env []) probe_envs=[Some [False],Some [False],Some [False],Some [False],Some [True],Some [True],Some [True],Some [True]]"
 by code_simp
lemma expr_not_empty_and: "compile (BNot (BAnd []))=[Conj 0,Neg]"
 by code_simp
lemma expr_not_empty_and_source_values:
 "map (\<lambda>env. eval_expr env (BNot (BAnd []))) probe_envs=[False,False,False,False,False,False,False,False]"
 by code_simp
lemma expr_not_empty_and_target_values:
 "map (\<lambda>env. run_code [Conj 0,Neg] env []) probe_envs=[Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [False],Some [False]]"
 by code_simp
lemma expr_nested_empty: "compile (BOr [(BAnd []),(BOr [])])=[Conj 0,Disj 0,Disj 2]"
 by code_simp
lemma expr_nested_empty_source_values:
 "map (\<lambda>env. eval_expr env (BOr [(BAnd []),(BOr [])])) probe_envs=[True,True,True,True,True,True,True,True]"
 by code_simp
lemma expr_nested_empty_target_values:
 "map (\<lambda>env. run_code [Conj 0,Disj 0,Disj 2] env []) probe_envs=[Some [True],Some [True],Some [True],Some [True],Some [True],Some [True],Some [True],Some [True]]"
 by code_simp
ML \<open>
 val checked = @{thms p_8c9a614d51b0_select_binding p_8c9a614d51b0_select_preserves p_8c9a614d51b0_step_binding p_8c9a614d51b0_step_preserves p_c7e96f0c096e_select_binding p_c7e96f0c096e_select_preserves p_c7e96f0c096e_step_binding p_c7e96f0c096e_step_preserves p_9eaa530b5825_select_binding p_9eaa530b5825_select_preserves p_9eaa530b5825_step_binding p_9eaa530b5825_step_preserves p_eb5a9d7915a6_select_binding p_eb5a9d7915a6_select_preserves p_eb5a9d7915a6_step_binding p_eb5a9d7915a6_step_preserves p_d864df79a77d_select_binding p_d864df79a77d_select_preserves p_d864df79a77d_step_binding p_d864df79a77d_step_preserves expr_true expr_true_source_values expr_true_target_values expr_false expr_false_source_values expr_false_target_values expr_atom expr_atom_source_values expr_atom_target_values expr_not_atom expr_not_atom_source_values expr_not_atom_target_values expr_double_not expr_double_not_source_values expr_double_not_target_values expr_triple_not expr_triple_not_source_values expr_triple_not_target_values expr_not_true expr_not_true_source_values expr_not_true_target_values expr_and_two expr_and_two_source_values expr_and_two_target_values expr_or_three expr_or_three_source_values expr_or_three_target_values expr_and_three expr_and_three_source_values expr_and_three_target_values expr_nested expr_nested_source_values expr_nested_target_values expr_repeated expr_repeated_source_values expr_repeated_target_values expr_seven_nots expr_seven_nots_source_values expr_seven_nots_target_values expr_empty_and expr_empty_and_source_values expr_empty_and_target_values expr_empty_or expr_empty_or_source_values expr_empty_or_target_values expr_unary_and expr_unary_and_source_values expr_unary_and_target_values expr_unary_or expr_unary_or_source_values expr_unary_or_target_values expr_not_empty_and expr_not_empty_and_source_values expr_not_empty_and_target_values expr_nested_empty expr_nested_empty_source_values expr_nested_empty_target_values};
 val _ = if Thm_Deps.has_skip_proof checked then error "Admitted dependency" else ();
 val _ = if null (Thm_Deps.all_oracles checked) then () else error "Oracle dependency";
 val audit = "Concrete bindings: no skipped proofs or oracle dependencies\n" ^ cat_lines (map (fn th => Thm_Name.print (Thm.get_name_hint th)) checked);
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "artifact-audit.txt")) [XML.Text audit];
\<close>
end
