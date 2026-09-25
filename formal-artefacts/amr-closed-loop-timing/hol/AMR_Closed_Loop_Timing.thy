theory AMR_Closed_Loop_Timing
  imports "AMR_Runtime_Binding.AMR_Runtime_Binding"
    "AMR_Extraction_Faithfulness.AMR_Artifacts"
    "AMR_Progress_Obligations.AMR_Progress"
begin

text \<open>Natural times are 10 ms plant ticks. A continuous physical event is
represented by the first integer plant tick at or after it, so the 9/169
bounds below start from that quantized event tick; measurement from the exact
continuous instant adds strictly less than one tick. These functions model
the fixed five-tick control/sample clock, five-tick sensor delivery and
ten-tick command delivery. They are an explicit timing contract, not a Python
semantics.\<close>

definition next5 :: "nat \<Rightarrow> nat" where
 "next5 n=5*((n+4) div 5)"
definition visible_time :: "nat \<Rightarrow> nat" where "visible_time n=next5 n+5"
definition release_time :: "nat \<Rightarrow> nat" where "release_time n=visible_time n"
definition start_waiting :: "nat \<Rightarrow> nat" where "start_waiting g=g+15"
definition start_braking :: "nat \<Rightarrow> nat \<Rightarrow> nat" where
 "start_braking g since=max (g+5) (next5 (since+149))+10"
definition brake_effect :: "nat \<Rightarrow> nat" where "brake_effect a=visible_time a+10"
definition finish_time :: "nat \<Rightarrow> nat" where "finish_time a=next5 (brake_effect a+149)"

lemma next5_grid: "next5 n mod 5=0"
 by (simp add:next5_def)

lemma next5_bounds: "n \<le> next5 n" "next5 n \<le> n+4"
 unfolding next5_def by presburger+

lemma observation_bound: "visible_time n \<le> n+9"
 using next5_bounds(2)[of n] by (simp add:visible_time_def)

lemma release_bound: "release_time n \<le> n+9"
 using observation_bound by (simp add:release_time_def)

lemma waiting_start_bound: "start_waiting g \<le> g+163"
 by (simp add:start_waiting_def)

lemma braking_start_bound:
 assumes "since\<le>g"
 shows "start_braking g since \<le> g+163"
proof -
 have "next5 (since+149) \<le> since+153" using next5_bounds(2)[of "since+149"] by simp
 then show ?thesis using assms by (simp add:start_braking_def max_def; presburger)
qed

lemma finish_time_exact: "finish_time a=next5 a+165"
proof -
 have grid: "next5 a mod 5=0" by (rule next5_grid)
 show ?thesis unfolding finish_time_def brake_effect_def visible_time_def next5_def
   using grid by presburger
qed

lemma finish_bound: "finish_time a \<le> a+169"
 using next5_bounds(2)[of a] by (simp add:finish_time_exact)

text \<open>The complete accepted source artifact is evaluated at stable-path
milestones. Atom numbers are fixed by the recorded vocabulary: 5 usable,
6 pedestrian, 7 owner, 8 released, 9 clear, 10 halted, 11 goal, 12 active,
14 Waiting, 15 Traversing, 16 BrakeRequested.\<close>

datatype milestone = MUnusable | MBrakingOwner | MHaltedOwner | MWaitingOwner
  | MClearOwner | MReleasedMotion | MGoalBrake | MGoalFinish

fun menv :: "milestone \<Rightarrow> nat \<Rightarrow> bool" where
 "menv MUnusable a=(a=12 \<or> a=15)"
| "menv MBrakingOwner a=(a=5 \<or> a=7 \<or> a=12 \<or> a=16)"
| "menv MHaltedOwner a=(a=5 \<or> a=7 \<or> a=10 \<or> a=12 \<or> a=16)"
| "menv MWaitingOwner a=(a=5 \<or> a=7 \<or> a=12 \<or> a=14)"
| "menv MClearOwner a=(a=5 \<or> a=7 \<or> a=9 \<or> a=12 \<or> a=15)"
| "menv MReleasedMotion a=(a=5 \<or> a=8 \<or> a=9 \<or> a=12 \<or> a=15)"
| "menv MGoalBrake a=(a=5 \<or> a=8 \<or> a=9 \<or> a=11 \<or> a=12 \<or> a=15)"
| "menv MGoalFinish a=(a=5 \<or> a=8 \<or> a=9 \<or> a=10 \<or> a=11 \<or> a=12 \<or> a=16)"

definition milestones where
 "milestones=[MUnusable,MBrakingOwner,MHaltedOwner,MWaitingOwner,
   MClearOwner,MReleasedMotion,MGoalBrake,MGoalFinish]"
definition milestone_outputs :: "(nat \<times> nat option) option list" where
 "milestone_outputs=[Some (5,Some 3),Some (5,Some 3),Some (4,Some 2),Some (4,Some 2),
   Some (7,Some 2),Some (4,Some 2),Some (5,Some 3),Some (8,Some 6)]"

lemma selected_source_milestones:
 "map (\<lambda>m. source_result (menv m) p_9eaa530b5825_step_source) milestones=milestone_outputs"
 by (simp add:milestones_def milestone_outputs_def p_9eaa530b5825_step_source_def)

lemma selected_target_milestones:
 "map (\<lambda>m. target_results (menv m) p_9eaa530b5825_step_target) milestones=
   map result_list milestone_outputs"
proof -
 have each: "\<And>m. target_results (menv m) p_9eaa530b5825_step_target=
   result_list (source_result (menv m) p_9eaa530b5825_step_source)"
   by (rule p_9eaa530b5825_step_preserves)
 have left: "map (\<lambda>m. target_results (menv m) p_9eaa530b5825_step_target) milestones=
   map (\<lambda>m. result_list (source_result (menv m) p_9eaa530b5825_step_source)) milestones"
   by (rule map_cong[OF refl]) (simp add:each)
 have right0: "map result_list
   (map (\<lambda>m. source_result (menv m) p_9eaa530b5825_step_source) milestones)=
   map result_list milestone_outputs"
   by (rule arg_cong[OF selected_source_milestones,
       where f="\<lambda>xs. map result_list xs"])
 have right: "map (\<lambda>m. result_list (source_result (menv m) p_9eaa530b5825_step_source)) milestones=
   map result_list milestone_outputs"
   using right0 by (simp only:map_map comp_def)
 show ?thesis using left right by simp
qed

text \<open>After the current owner releases, the previously unserved registered
robot is the only legal choice. Validate followed by Commit grants it, regardless
of the advisory value. The theorem assumes the other request remains registered.\<close>
fun other where "other A=B" | "other B=A"

lemma other_simps:
 "other r\<noteq>r" "other (other r)=r"
 by (cases r; simp)+

lemma robot_not_eq_other: "x\<noteq>r \<Longrightarrow> x=other r"
 by (cases r; cases x; simp)

theorem release_select_commit_grants_other:
 fixes advice :: "robot option"
 assumes "owner s=Some r" "requested s (other r)" "\<not>requested s r"
   "fresh s" "\<not>blocked s" "pending s=None"
 defines "u \<equiv> fst (step s (Release r True))"
 defines "v \<equiv> fst (step u (Validate (select u advice)))"
 shows "snd (step v Commit)=Some (Grant (other r))"
 using assms by (cases r; cases advice)
   (auto simp:u_def v_def commit_def legal_def usable_def requested_alt set_req_alt
     dest:robot_not_eq_other split:if_splits)

text \<open>Composition uses proved local scheduler bounds and the imported
3,100-tick exact-reference travel service. The service inequalities remain
explicit premises: no hardware or arbitrary-environment deadline follows.\<close>
theorem stable_two_task_completion_bound:
 fixes g1 s1 a1 f1 g2 s2 a2 f2 :: nat
 assumes "g1\<le>10" "s1\<le>g1+163" "a1\<le>s1+3100" "f1\<le>a1+169"
   "g2\<le>f1+10" "s2\<le>g2+163" "a2\<le>s2+3100" "f2\<le>a2+169"
 shows "f2\<le>6884"
 using assms by presburger

lemma stable_bound_seconds: "(6884::rat)/100=1721/25"
 by simp

definition timing_rows :: "integer list list" where
 "timing_rows=map (\<lambda>n. map integer_of_nat [n,next5 n,visible_time n,release_time n,finish_time n]) [0..<5]"
definition source_rows :: "integer list list" where
 "source_rows=map (\<lambda>m. case source_result (menv m) p_9eaa530b5825_step_source of
    None \<Rightarrow> [-1,-1] | Some (a,None) \<Rightarrow> [integer_of_nat a,-1]
    | Some (a,Some n) \<Rightarrow> [integer_of_nat a,integer_of_nat n]) milestones"

ML \<open>
 val checked = @{thms next5_grid next5_bounds observation_bound release_bound waiting_start_bound
   braking_start_bound finish_time_exact finish_bound selected_source_milestones
   selected_target_milestones other_simps release_select_commit_grants_other
   stable_two_task_completion_bound stable_bound_seconds};
 val _ = if Thm_Deps.has_skip_proof checked then error "Admitted dependency" else ();
 val _ = if null (Thm_Deps.all_oracles checked) then () else error "Oracle dependency";
 val audit = "No skipped proofs or oracle dependencies\n" ^
   cat_lines (map (fn th => Thm_Name.print (Thm.get_name_hint th)) checked);
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "timing-proof-audit.txt")) [XML.Text audit];
 fun csv rows = cat_lines (map (space_implode "," o map IntInf.toString) rows);
 val timing = @{code timing_rows};
 val source = @{code source_rows};
 val _ = if length timing=5 andalso length source=8 then () else error "Unexpected export size";
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "timing.csv")) [XML.Text (csv timing)];
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "source.csv")) [XML.Text (csv source)];
\<close>
end
