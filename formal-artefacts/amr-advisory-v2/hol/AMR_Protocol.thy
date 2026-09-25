theory AMR_Protocol
  imports "Bridge_Algebra_Repair.Bridge_Trace_Repair"
begin

datatype robot = A | B
datatype input = Register robot | Observe bool bool | Validate "robot option" | Commit
 | Issue robot | Apply | Release robot bool | Service "robot option"
 | RequestAdvice | Reply "robot option" | Consume "robot option"
datatype visible = Registered robot | Observed bool bool | Grant robot | Issued robot
 | Proceed robot | Released robot
record core =
 req_a :: bool
 req_b :: bool
 owner :: "robot option"
 blocked :: bool
 fresh :: bool
 pending :: "robot option"
 command :: "robot option"
definition initial :: core where
 "initial = \<lparr>req_a=False,req_b=False,owner=None,blocked=False,fresh=True,pending=None,command=None\<rparr>"
fun requested :: "core \<Rightarrow> robot \<Rightarrow> bool" where
 "requested s A = req_a s" | "requested s B = req_b s"
fun set_req :: "core \<Rightarrow> robot \<Rightarrow> bool \<Rightarrow> core" where
 "set_req s A b = s\<lparr>req_a:=b\<rparr>" | "set_req s B b = s\<lparr>req_b:=b\<rparr>"
definition usable where "usable s = (\<not> blocked s \<and> fresh s)"
definition legal where "legal s r = (requested s r \<and> owner s=None \<and> usable s)"
fun validate where
 "validate s None = s"
| "validate s (Some r) = (if pending s=None \<and> legal s r then s\<lparr>pending:=Some r\<rparr> else s)"
definition commit where
 "commit s = (case pending s of None \<Rightarrow> (s,None) | Some r \<Rightarrow>
  if legal s r then ((set_req s r False)\<lparr>owner:=Some r,pending:=None\<rparr>,Some (Grant r))
  else (s\<lparr>pending:=None\<rparr>,None))"
fun step :: "core \<Rightarrow> input \<Rightarrow> core \<times> visible option" where
 "step s (Register r) = (set_req s r True,Some (Registered r))"
| "step s (Observe b f) = (s\<lparr>blocked:=b,fresh:=f,pending:=pending s,command:=command s\<rparr>,Some (Observed b f))"
| "step s (Validate i) = (validate s i,None)"
| "step s Commit = commit s"
| "step s (Issue r) = (if owner s=Some r \<and> usable s then (s\<lparr>command:=Some r\<rparr>,Some (Issued r)) else (s,None))"
| "step s Apply = (case command s of None \<Rightarrow> (s,None) | Some r \<Rightarrow>
 (s\<lparr>command:=None\<rparr>,if owner s=Some r \<and> usable s then Some (Proceed r) else None))"
| "step s (Release r clear) = (if owner s=Some r \<and> clear then (s\<lparr>owner:=None,command:=None\<rparr>,Some (Released r)) else (s,None))"
| "step s (Service i) = (if pending s=None then (validate s i,None) else commit s)"
| "step s RequestAdvice = (s,None)"
| "step s (Reply r) = (s,None)"
| "step s (Consume r) = (s,None)"

record reference =
 rr_a :: bool
 rr_b :: bool
 r_owner :: "robot option"
 r_blocked :: bool
 r_fresh :: bool
fun r_req where "r_req s A=rr_a s" | "r_req s B=rr_b s"
fun r_set where "r_set s A b=s\<lparr>rr_a:=b\<rparr>" | "r_set s B b=s\<lparr>rr_b:=b\<rparr>"
definition abs_state where
 "abs_state s=\<lparr>rr_a=req_a s,rr_b=req_b s,r_owner=owner s,r_blocked=blocked s,r_fresh=fresh s\<rparr>"
definition ref_initial :: reference where
 "ref_initial=\<lparr>rr_a=False,rr_b=False,r_owner=None,r_blocked=False,r_fresh=True\<rparr>"
lemma initial_simulation: "abs_state initial=ref_initial"
 by (simp add:abs_state_def initial_def ref_initial_def)
fun ref_step :: "reference \<Rightarrow> visible \<Rightarrow> reference option" where
 "ref_step s (Registered r)=Some (r_set s r True)"
| "ref_step s (Observed b f)=Some (s\<lparr>r_blocked:=b,r_fresh:=f\<rparr>)"
| "ref_step s (Grant r)=(if r_req s r \<and> r_owner s=None \<and> \<not> r_blocked s \<and> r_fresh s then Some ((r_set s r False)\<lparr>r_owner:=Some r\<rparr>) else None)"
| "ref_step s (Issued r)=(if r_owner s=Some r \<and> \<not> r_blocked s \<and> r_fresh s then Some s else None)"
| "ref_step s (Proceed r)=(if r_owner s=Some r \<and> \<not> r_blocked s \<and> r_fresh s then Some s else None)"
| "ref_step s (Released r)=(if r_owner s=Some r then Some (s\<lparr>r_owner:=None\<rparr>) else None)"
fun ref_run where
 "ref_run s []=Some s"
| "ref_run s (e#es)=(case ref_step s e of None \<Rightarrow> None | Some t \<Rightarrow> ref_run t es)"
fun one where "one None=[]" | "one (Some e)=[e]"
lemma set_req_alt: "set_req s r b=(if r=A then s\<lparr>req_a:=b\<rparr> else s\<lparr>req_b:=b\<rparr>)"
 by (cases r) auto
lemma r_set_alt: "r_set s r b=(if r=A then s\<lparr>rr_a:=b\<rparr> else s\<lparr>rr_b:=b\<rparr>)"
 by (cases r) auto
lemma requested_alt: "requested s r=(if r=A then req_a s else req_b s)"
 by (cases r) auto
lemma r_req_alt: "r_req s r=(if r=A then rr_a s else rr_b s)"
 by (cases r) auto
lemma validate_alt: "validate s i=(case i of None \<Rightarrow> s | Some r \<Rightarrow> if pending s=None \<and> legal s r then s\<lparr>pending:=Some r\<rparr> else s)"
 by (cases i) auto
lemma step_simulation:
 "ref_run (abs_state s) (one (snd (step s i)))=Some (abs_state (fst (step s i)))"
 by (cases i; auto simp: abs_state_def commit_def usable_def legal_def set_req_alt r_set_alt requested_alt r_req_alt validate_alt
     split: option.splits robot.splits if_splits)

fun run_state where "run_state s []=s" | "run_state s (i#is)=run_state (fst (step s i)) is"
fun run_visible where "run_visible s []=[]" | "run_visible s (i#is)=one (snd (step s i)) @ run_visible (fst (step s i)) is"
lemma ref_append:
 "ref_run s (xs@ys)=(case ref_run s xs of None \<Rightarrow> None | Some t \<Rightarrow> ref_run t ys)"
 by (induction xs arbitrary:s) (auto split:option.splits)
theorem finite_word_simulation:
 "ref_run (abs_state s) (run_visible s xs)=Some (abs_state (run_state s xs))"
 by (induction xs arbitrary:s) (simp_all add:ref_append step_simulation)

text \<open>Full events have unique provenance; trusted internal steps remain on the trusted side.\<close>
datatype event = Trusted input "visible option" | Provider "robot option"
fun is_trusted where "is_trusted (Trusted i v)=True" | "is_trusted (Provider r)=False"
fun is_visible where "is_visible (Trusted i (Some v))=True" | "is_visible _=False"
fun visible_of where "visible_of (Trusted i v)=one v" | "visible_of (Provider r)=[]"
fun open_next :: "core \<Rightarrow> event \<Rightarrow> core option" where
 "open_next s (Trusted i v)=(if (\<forall>r. i \<noteq> Reply r) \<and> snd (step s i)=v then Some (fst (step s i)) else None)"
| "open_next s (Provider r)=None"
fun accepts where
 "accepts k s []=True"
| "accepts k s (e#es)=(case k s e of None \<Rightarrow> False | Some t \<Rightarrow> accepts k t es)"
record mailbox =
 registered :: bool
 slot :: "robot option"
definition m_initial where "m_initial=\<lparr>registered=False,slot=None\<rparr>"
fun causal_next :: "mailbox \<Rightarrow> event \<Rightarrow> mailbox option" where
 "causal_next m (Provider r)=Some (if registered m \<and> slot m=None \<and> r\<noteq>None then m\<lparr>slot:=r\<rparr> else m)"
| "causal_next m (Trusted RequestAdvice v)=Some (m\<lparr>registered:=True\<rparr>)"
| "causal_next m (Trusted (Consume r) v)=(if r=slot m then Some m else None)"
| "causal_next m (Trusted i v)=Some m"
fun system_next :: "core \<times> mailbox \<Rightarrow> event \<Rightarrow> (core \<times> mailbox) option" where
 "system_next (s,m) (Provider r)=(case causal_next m (Provider r) of None \<Rightarrow> None | Some n \<Rightarrow> Some (s,n))"
| "system_next (s,m) (Trusted i v)=(case open_next s (Trusted i v) of None \<Rightarrow> None | Some t \<Rightarrow>
  (case causal_next m (Trusted i v) of None \<Rightarrow> None | Some n \<Rightarrow> Some (t,n)))"
definition P_open where "P_open={es. accepts open_next initial es}"
definition D where "D={es. \<forall>e\<in>set es. \<not> is_trusted e}"
definition K_T where "K_T={es. accepts causal_next m_initial es}"
definition S_HOL where "S_HOL={es. accepts system_next (initial,m_initial) es}"
definition G_T where "G_T X=X \<inter> K_T"
definition V where "V={e. is_visible e}"
definition P_ref where "P_ref={es. \<exists>r. ref_run ref_initial (concat (map visible_of es))=Some r}"
lemma system_decomposition:
 "accepts system_next (s,m) es \<Longrightarrow>
  accepts open_next s (filter is_trusted es) \<and> accepts causal_next m es"
proof (induction es arbitrary:s m)
 case Nil then show ?case by simp
next
 case (Cons e es) then show ?case
  by (cases e) (auto split:option.splits prod.splits if_splits)
qed
lemma split_interleaves:
 "interleaves (filter is_trusted es) (filter (\<lambda>e. \<not> is_trusted e) es) es"
 by (induction es) (auto intro:interleaves.intros)
theorem operational_embedding:
 "S_HOL \<subseteq> G_T (trace_parallel P_open D)"
proof
 fix es assume "es\<in>S_HOL"
 then have dec: "accepts open_next initial (filter is_trusted es)" "accepts causal_next m_initial es"
  using system_decomposition by (auto simp:S_HOL_def)
 have l: "filter is_trusted es\<in>P_open" using dec by (simp add:P_open_def)
 have r: "filter (\<lambda>e. \<not> is_trusted e) es\<in>D" by (auto simp:D_def)
 have "es\<in>trace_parallel P_open D"
  using l r split_interleaves[of es] unfolding trace_parallel_def by blast
 then show "es\<in>G_T (trace_parallel P_open D)" using dec by (simp add:G_T_def K_T_def)
qed
lemma visible_trusted: "is_visible e \<Longrightarrow> is_trusted e"
 by (cases e rule:is_visible.cases) auto
lemma hidden_no_visible: "\<not> is_visible e \<Longrightarrow> visible_of e=[]"
 by (cases e rule:is_visible.cases) auto
lemma provider_silent:
 "\<forall>ys\<in>D. filter (\<lambda>e. e\<in>V) ys=[]"
 by (auto simp:D_def V_def filter_empty_conv dest:visible_trusted)
theorem component_authority:
 "project V (G_T (trace_parallel P_open D)) \<subseteq> project V P_open"
 by (rule authority_boundary_traces[OF provider_silent]) (auto simp:G_T_def)
lemma open_simulation:
 "accepts open_next s es \<Longrightarrow> \<exists>r. ref_run (abs_state s) (concat (map visible_of es))=Some r"
proof (induction es arbitrary:s)
 case Nil then show ?case by simp
next
 case (Cons e es)
 obtain i v where e:"e=Trusted i v" using Cons.prems by (cases e) auto
 have v:"snd (step s i)=v" and tail:"accepts open_next (fst (step s i)) es"
   using Cons.prems e by (auto split:if_splits)
 show ?case using Cons.IH[OF tail] step_simulation[of s i]
   by (simp add:e ref_append v)
qed
lemma visible_filter:
 "concat (map visible_of (filter (\<lambda>e. e\<in>V) es))=concat (map visible_of es)"
 by (induction es) (auto simp:V_def dest:hidden_no_visible)
theorem open_authority: "project V P_open \<subseteq> P_ref"
 using open_simulation[of initial] by (auto simp:project_def P_open_def P_ref_def visible_filter initial_simulation)
theorem system_authority: "project V S_HOL \<subseteq> P_ref"
 using project_mono[OF operational_embedding] component_authority open_authority by blast

fun select :: "core \<Rightarrow> robot option \<Rightarrow> robot option" where
 "select s a=(if a\<noteq>None \<and> (case a of Some r \<Rightarrow> legal s r | None \<Rightarrow> False) then a
 else if legal s A then Some A else if legal s B then Some B else None)"
lemma selector_total_legal:
 "(\<exists>r. legal s r) \<Longrightarrow> \<exists>r. select s a=Some r \<and> legal s r"
proof -
 assume "\<exists>r. legal s r"
 then have "legal s A \<or> legal s B" by (metis robot.exhaust)
 then show ?thesis by (auto split:option.splits if_splits)
qed

text \<open>The source-restricted machine latches the mailbox-derived selector atomically at an empty pending choice. Consume is read-only bookkeeping.\<close>
fun source_ok where
 "source_ok s m (Trusted (Service i) v)=(pending s\<noteq>None \<or> i=select s (slot m))"
| "source_ok s m (Trusted (Validate i) v)=(pending s\<noteq>None \<or> i=select s (slot m))"
| "source_ok s m e=True"
definition source_next where
 "source_next sm e=(if source_ok (fst sm) (snd sm) e then system_next sm e else None)"
definition S_source where "S_source={es. accepts source_next (initial,m_initial) es}"
lemma source_accepts_broad:
 "accepts source_next sm es \<Longrightarrow> accepts system_next sm es"
 by (induction es arbitrary:sm) (auto simp:source_next_def split:if_splits option.splits)
theorem source_inclusion: "S_source\<subseteq>S_HOL"
 using source_accepts_broad by (auto simp:S_source_def S_HOL_def)
theorem source_authority: "project V S_source\<subseteq>P_ref"
 using project_mono[OF source_inclusion] system_authority by blast
lemma source_latch_binding:
 assumes "pending s=None" "i=Service intent \<or> i=Validate intent"
  "source_next (s,m) (Trusted i v)=Some (t,n)"
 shows "intent=select s (slot m) \<and> t=validate s intent \<and> n=m"
 using assms by (auto simp:source_next_def split:if_splits)
lemma source_service_effect:
 assumes "source_next (s,m) (Trusted (Service i) v)=Some (t,n)"
 shows "(t,v)=step s (Service (select s (slot m)))"
 using assms by (auto simp:source_next_def split:if_splits)
lemma source_provider_preserves_pending:
 "source_next (s,m) (Provider a)=Some (t,n) \<Longrightarrow> pending t=pending s"
 by (auto simp:source_next_def)
lemma selected_pending:
 assumes "pending s=None" "\<exists>r. legal s r"
 shows "pending (validate s (select s a))=select s a"
proof -
 obtain r where "select s a=Some r" "legal s r" using selector_total_legal[OF assms(2)] by blast
 then show ?thesis using assms(1) by (simp only:validate.simps) simp
qed
lemma source_latch_choice:
 assumes "pending s=None" "\<exists>r. legal s r" "i=Service intent \<or> i=Validate intent"
  "source_next (s,m) (Trusted i v)=Some (t,n)"
 shows "pending t=select s (slot m)"
 using source_latch_binding[OF assms(1,3,4)] selected_pending[OF assms(1,2)] by metis
lemma source_advice_response:
 "legal s r \<Longrightarrow> select s (Some r)=Some r"
 by simp
lemma source_fifo_response:
 "select s None=(if legal s A then Some A else if legal s B then Some B else None)"
 by simp
lemma validated_choice_frozen:
 "pending s=Some r \<Longrightarrow> validate s i=s"
 by (cases i) auto
lemma persistent_consume:
 "causal_next m (Trusted (Consume (slot m)) v)=Some m"
 by simp
lemma repeated_consume:
 "accepts causal_next m (replicate n (Trusted (Consume (slot m)) None))"
 by (induction n) simp_all
lemma service_progress:
 assumes "pending s=None" "legal s r"
 shows "snd (step (fst (step s (Service (Some r)))) (Service i))=Some (Grant r)"
 using assms by (simp add:legal_def usable_def commit_def requested_alt)
lemma pending_commit_progress:
 "pending s=Some r \<Longrightarrow> legal s r \<Longrightarrow> snd (step s (Service i))=Some (Grant r)"
 by (simp add:commit_def)
lemma advice_does_not_reset:
 "fst (step s (Reply a))=s" "fst (step s (Consume a))=s"
 "fst (step s RequestAdvice)=s"
 "usable s \<Longrightarrow> fst (step s (Observe False True))=s"
 by (auto simp:usable_def)
fun benign where
 "benign (Reply r)=True" | "benign (Consume r)=True" | "benign RequestAdvice=True"
| "benign (Observe False True)=True" | "benign _=False"
lemma benign_step:
 "usable s \<Longrightarrow> benign i \<Longrightarrow> fst (step s i)=s"
 by (cases i rule:benign.cases) (auto simp:usable_def)
lemma benign_preserves:
 "usable s \<Longrightarrow> list_all benign xs \<Longrightarrow> run_state s xs=s"
 by (induction xs arbitrary:s) (auto simp:benign_step)
theorem conditional_authorization_progress:
 assumes "pending s=None" "\<exists>r. legal s r" "list_all benign xs"
 shows "\<exists>r. snd (step (run_state (fst (step s (Service (select s advice)))) xs) (Service arbitrary_intent))=Some (Grant r)"
proof -
 obtain r where chosen: "select s advice=Some r" "legal s r"
  using selector_total_legal[OF assms(2),of advice] by blast
 have use: "usable (fst (step s (Service (Some r))))"
  using chosen assms by (simp add:legal_def usable_def)
 have unchanged: "run_state (fst (step s (Service (Some r)))) xs=fst (step s (Service (Some r)))"
  by (rule benign_preserves[OF use assms(3)])
 have "snd (step (run_state (fst (step s (Service (select s advice)))) xs) (Service arbitrary_intent))=Some (Grant r)"
  using service_progress[OF assms(1) chosen(2),of arbitrary_intent]
  by (simp only:chosen(1) unchanged)
 then show ?thesis by blast
qed


text \<open>Each service round has an arbitrary finite benign gap and a universally quantified advisory value. Evaluation stops at the first Grant, so no stability premise is imposed after Grant.\<close>
fun grant_event where "grant_event (Some (Grant r))=True" | "grant_event _=False"
fun grants_within :: "core \<Rightarrow> (input list \<times> robot option) list \<Rightarrow> bool" where
 "grants_within s []=False"
| "grants_within s ((gap,a)#rounds)=(let t=run_state s gap; u=step t (Service (select t a)) in
 if grant_event (snd u) then True else grants_within (fst u) rounds)"
lemma empty_pending_two_rounds:
 assumes "pending s=None" "\<exists>r. legal s r"
  "list_all benign g1" "list_all benign g2"
 shows "grants_within s [(g1,a1),(g2,a2)]"
proof -
 obtain r where sel:"select s a1=Some r" "legal s r" using selector_total_legal[OF assms(2)] by blast
 have us:"usable s" using sel by (simp add:legal_def)
 have gap:"run_state s g1=s" by (rule benign_preserves[OF us assms(3)])
 have val:"fst (step s (Service (select s a1)))=s\<lparr>pending:=Some r\<rparr>"
  using assms(1) sel by (simp only:sel(1) step.simps) simp
 have us2:"usable (s\<lparr>pending:=Some r\<rparr>)" using us by (simp add:usable_def)
 have gap2:"run_state (s\<lparr>pending:=Some r\<rparr>) g2=s\<lparr>pending:=Some r\<rparr>"
  by (rule benign_preserves[OF us2 assms(4)])
 show ?thesis using assms(1) sel
  by (simp add:Let_def gap val gap2 commit_def legal_def usable_def requested_alt)
qed
lemma grants_within_append:
 "grants_within s xs \<Longrightarrow> grants_within s (xs@ys)"
 by (induction xs arbitrary:s) (auto split:prod.splits simp:Let_def)
theorem authorization_from_any_pending:
 assumes "\<exists>r. legal s r" "list_all benign g1" "list_all benign g2" "list_all benign g3"
 shows "grants_within s [(g1,a1),(g2,a2),(g3,a3)]"
proof (cases "pending s")
 case None
 have "grants_within s [(g1,a1),(g2,a2)]" by (rule empty_pending_two_rounds[OF None assms(1,2,3)])
 then show ?thesis using grants_within_append[of s "[(g1,a1),(g2,a2)]" "[(g3,a3)]"] by simp
next
 case (Some r)
 have us:"usable s" using assms(1) by (auto simp:legal_def)
 have gap:"run_state s g1=s" by (rule benign_preserves[OF us assms(2)])
 show ?thesis
 proof (cases "legal s r")
  case True then show ?thesis using Some by (simp add:Let_def gap commit_def)
 next
  case False
  have eq:"\<And>x. legal (s\<lparr>pending:=None\<rparr>) x=legal s x"
   by (simp add:legal_def usable_def requested_alt)
  have available:"\<exists>r. legal (s\<lparr>pending:=None\<rparr>) r"
   using assms(1) by (simp only:eq)
  have tail:"grants_within (s\<lparr>pending:=None\<rparr>) [(g2,a2),(g3,a3)]"
   by (rule empty_pending_two_rounds[OF _ available assms(3,4)]) simp
  show ?thesis using Some False tail by (simp add:Let_def gap commit_def)
 qed
qed

definition wait_step where "wait_step s advice=(if advice=None then s else fst (step s (Service (select s advice))))"
lemma wait_forever: "((\<lambda>t. wait_step t None) ^^ n) s=s"
 by (induction n) (simp_all add:wait_step_def)
text \<open>The wait state is unchanged at every natural index despite infinitely many services; every finite visible prefix is empty and reference-accepted.\<close>
lemma wait_safety: "ref_run (abs_state s) []=Some (abs_state s)" by simp

definition both where "both=initial\<lparr>req_a:=True,req_b:=True\<rparr>"
lemma advice_witnesses:
 "select both (Some A)=Some A" "select both (Some B)=Some B" "select both None=Some A"
 by (simp_all add:both_def initial_def legal_def usable_def)
lemma e3a:
 "snd (step (run_state both [Validate (Some A),Observe True True]) Commit)=None"
 by (simp add:both_def initial_def legal_def usable_def commit_def)
lemma e3b:
 "snd (step (run_state both [Validate (Some A),Commit,Issue A,Observe True True]) Apply)=None"
 by (simp add:both_def initial_def legal_def usable_def commit_def)



definition unchecked_commit where
 "unchecked_commit s=(case pending s of None \<Rightarrow> None | Some r \<Rightarrow> Some (Grant r))"
definition unchecked_apply where
 "unchecked_apply s=(case command s of None \<Rightarrow> None | Some r \<Rightarrow> Some (Proceed r))"
lemma e3a_fault:
 "unchecked_commit (run_state both [Validate (Some A),Observe True True])=Some (Grant A)"
 "\<not> legal (run_state both [Validate (Some A),Observe True True]) A"
 by (simp_all add:unchecked_commit_def both_def initial_def legal_def usable_def)
lemma e3b_fault:
 "unchecked_apply (run_state both [Validate (Some A),Commit,Issue A,Observe True True])=Some (Proceed A)"
 "\<not> usable (run_state both [Validate (Some A),Commit,Issue A,Observe True True])"
 by (simp_all add:unchecked_apply_def both_def initial_def legal_def usable_def commit_def)

definition robots where "robots=[A,B]"
definition opts where "opts=[None,Some A,Some B]"
definition bools where "bools=[False,True]"
definition all_states where
 "all_states=concat (map (\<lambda>a. concat (map (\<lambda>b. concat (map (\<lambda>own. concat (map (\<lambda>x. concat (map (\<lambda>f. concat (map (\<lambda>p. map (\<lambda>c. \<lparr>req_a=a,req_b=b,owner=own,blocked=x,fresh=f,pending=p,command=c\<rparr>) opts) opts)) bools)) bools)) opts)) bools)) bools)"
definition all_inputs where
 "all_inputs=map Register robots @ concat (map (\<lambda>b. map (Observe b) bools) bools) @ map Validate opts @ [Commit] @ map Issue robots @ [Apply] @ concat (map (\<lambda>r. map (Release r) bools) robots) @ map Service opts @ [RequestAdvice] @ map Reply opts @ map Consume opts"
fun enc_r :: "robot option \<Rightarrow> integer" where
 "enc_r None=0" | "enc_r (Some A)=1" | "enc_r (Some B)=2"
definition enc_b :: "bool \<Rightarrow> integer" where "enc_b b=(if b then 1 else 0)"
definition enc_s where "enc_s s=[enc_b (req_a s),enc_b (req_b s),enc_r (owner s),enc_b (blocked s),enc_b (fresh s),enc_r (pending s),enc_r (command s)]"
fun enc_v :: "visible option \<Rightarrow> integer list" where
 "enc_v None=[0,0,0]"
| "enc_v (Some (Registered r))=[1,enc_r (Some r),0]"
| "enc_v (Some (Observed b f))=[2,enc_b b,enc_b f]"
| "enc_v (Some (Grant r))=[3,enc_r (Some r),0]"
| "enc_v (Some (Issued r))=[4,enc_r (Some r),0]"
| "enc_v (Some (Proceed r))=[5,enc_r (Some r),0]"
| "enc_v (Some (Released r))=[6,enc_r (Some r),0]"
definition export_rows where
 "export_rows=concat (map (\<lambda>s. map (\<lambda>i. enc_s s @ enc_s (fst (step s i)) @ enc_v (snd (step s i))) all_inputs) all_states)"
definition selector_rows where
 "selector_rows=concat (map (\<lambda>s. map (\<lambda>a. enc_s s @ [enc_r a,enc_r (select s a)]) opts) all_states)"
ML \<open>
 val selection = @{code selector_rows};
 val selbody = cat_lines (map (space_implode "," o map IntInf.toString) selection);
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "selector.csv")) [XML.Text selbody];
 val rows = @{code export_rows};
 val body = cat_lines (map (space_implode "," o map IntInf.toString) rows);
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "core-transitions.csv")) [XML.Text body];
 val _ = writeln ("EXPORT: " ^ Int.toString (length rows) ^ " HOL-evaluated core transition rows");
\<close>

ML \<open>
 val checked = @{thms initial_simulation step_simulation finite_word_simulation operational_embedding
 component_authority open_authority system_authority conditional_authorization_progress
 wait_forever wait_safety advice_witnesses e3a e3b e3a_fault e3b_fault
 source_inclusion source_authority source_latch_binding source_latch_choice source_service_effect source_provider_preserves_pending
 source_advice_response source_fifo_response validated_choice_frozen persistent_consume repeated_consume authorization_from_any_pending};
 val _ = if Thm_Deps.has_skip_proof checked then error "Admitted dependency" else ();
 val _ = if null (Thm_Deps.all_oracles checked) then writeln "AUDIT: AMR targets have no skipped proofs or oracle dependencies" else error "Oracle dependency";
 val audit = "AMR headline results: no skipped proofs; no oracle dependencies\n" ^
   cat_lines (map (fn th => Thm_Name.print (Thm.get_name_hint th)) checked);
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "proof-audit.txt")) [XML.Text audit];
\<close>
end



