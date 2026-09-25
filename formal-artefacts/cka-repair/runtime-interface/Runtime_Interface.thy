theory Runtime_Interface
  imports "Bridge_Algebra_Repair.Bridge_Trace_Repair"
begin

text \<open>A finite protocol for one logical operation. The service checks the
current permission and records its effect atomically with completion. LostAck
is a lost notification after that atomic step, not an uncertain remote commit.\<close>

datatype phase = Idle | Pending | Approved | Completed
datatype command = Submit | Service | SetPermission bool | Advice bool | LostAck | Poll
datatype event = Policy bool | Commit | Hidden command

record istate =
  permitted :: bool
  stage :: phase
  advice_available :: bool

definition initial :: istate where
  "initial = \<lparr>permitted = True, stage = Idle, advice_available = False\<rparr>"

fun step :: "istate \<Rightarrow> command \<Rightarrow> istate \<times> event" where
  "step s Submit =
    (s\<lparr>stage := (if stage s = Idle then Pending else stage s)\<rparr>, Hidden Submit)"
| "step s Service =
    (if stage s = Pending \<and> permitted s then
       (s\<lparr>stage := Approved\<rparr>, Hidden Service)
     else if stage s = Approved \<and> permitted s then
       (s\<lparr>stage := Completed\<rparr>, Commit)
     else (s, Hidden Service))"
| "step s (SetPermission b) = (s\<lparr>permitted := b\<rparr>, Policy b)"
| "step s (Advice b) = (s\<lparr>advice_available := b\<rparr>, Hidden (Advice b))"
| "step s LostAck = (s, Hidden LostAck)"
| "step s Poll = (s, Hidden Poll)"

fun run_state :: "(istate \<Rightarrow> command \<Rightarrow> istate \<times> event)
    \<Rightarrow> istate \<Rightarrow> command list \<Rightarrow> istate" where
  "run_state k s [] = s"
| "run_state k s (c # cs) = run_state k (fst (k s c)) cs"

fun run_trace :: "(istate \<Rightarrow> command \<Rightarrow> istate \<times> event)
    \<Rightarrow> istate \<Rightarrow> command list \<Rightarrow> event list" where
  "run_trace k s [] = []"
| "run_trace k s (c # cs) = snd (k s c) # run_trace k (fst (k s c)) cs"

fun controlled :: "event \<Rightarrow> bool" where
  "controlled (Policy b) = True"
| "controlled Commit = True"
| "controlled (Hidden c) = False"

definition control_alphabet :: "event set" where
  "control_alphabet = {e. controlled e}"

definition abstract_state :: "istate \<Rightarrow> bool \<times> bool" where
  "abstract_state s = (permitted s, stage s = Completed)"

fun ref_step :: "bool \<times> bool \<Rightarrow> event \<Rightarrow> (bool \<times> bool) option" where
  "ref_step r (Policy b) = Some (b, snd r)"
| "ref_step r Commit = (if fst r \<and> \<not> snd r then Some (fst r, True) else None)"
| "ref_step r (Hidden c) = None"

fun ref_run :: "bool \<times> bool \<Rightarrow> event list \<Rightarrow> (bool \<times> bool) option" where
  "ref_run r [] = Some r"
| "ref_run r (e # es) = (case ref_step r e of None \<Rightarrow> None | Some r' \<Rightarrow> ref_run r' es)"

lemma step_simulation:
  "ref_run (abstract_state s) (filter controlled [snd (step s c)]) =
    Some (abstract_state (fst (step s c)))"
  by (cases "stage s"; cases c) (auto simp: abstract_state_def)

lemma ref_run_append:
  "ref_run r (xs @ ys) =
    (case ref_run r xs of None \<Rightarrow> None | Some r' \<Rightarrow> ref_run r' ys)"
  by (induction xs arbitrary: r) (auto split: option.splits)

theorem runtime_refinement:
  "ref_run (abstract_state s) (filter controlled (run_trace step s cs)) =
    Some (abstract_state (run_state step s cs))"
proof (induction cs arbitrary: s)
  case Nil
  then show ?case by simp
next
  case (Cons c cs)
  have split_trace: "filter controlled (run_trace step s (c # cs)) =
    filter controlled [snd (step s c)] @ filter controlled (run_trace step (fst (step s c)) cs)"
    by simp
  show ?case
    by (simp only: split_trace ref_run_append step_simulation option.case run_state.simps Cons.IH)
qed

lemma run_state_append:
  "run_state k s (xs @ ys) = run_state k (run_state k s xs) ys"
  by (induction xs arbitrary: s) auto

lemma run_trace_append:
  "run_trace k s (xs @ ys) = run_trace k s xs @ run_trace k (run_state k s xs) ys"
  by (induction xs arbitrary: s) auto

definition canonical :: "bool \<times> bool \<Rightarrow> istate" where
  "canonical r = \<lparr>permitted = fst r, stage = (if snd r then Completed else Idle), advice_available = False\<rparr>"

fun lift_event :: "event \<Rightarrow> command list" where
  "lift_event (Policy b) = [SetPermission b]"
| "lift_event Commit = [Submit, Service, Service]"
| "lift_event (Hidden c) = []"

definition lift_events :: "event list \<Rightarrow> command list" where
  "lift_events es = concat (map lift_event es)"

lemma reference_step_lifting:
  assumes "ref_step r e = Some r'"
  shows "run_state step (canonical r) (lift_event e) = canonical r' \<and>
    filter controlled (run_trace step (canonical r) (lift_event e)) = [e]"
  using assms
  by (cases r; cases e) (auto simp: canonical_def split: if_splits)

theorem reference_lifting:
  assumes "ref_run r es = Some r'"
  shows "run_state step (canonical r) (lift_events es) = canonical r' \<and>
    filter controlled (run_trace step (canonical r) (lift_events es)) = es"
  using assms
proof (induction es arbitrary: r r')
  case Nil
  then show ?case by (simp add: lift_events_def)
next
  case (Cons e es)
  then obtain middle where one: "ref_step r e = Some middle"
    and rest: "ref_run middle es = Some r'"
    by (auto split: option.splits)
  have first: "run_state step (canonical r) (lift_event e) = canonical middle \<and>
    filter controlled (run_trace step (canonical r) (lift_event e)) = [e]"
    by (rule reference_step_lifting[OF one])
  have tail: "run_state step (canonical middle) (lift_events es) = canonical r' \<and>
    filter controlled (run_trace step (canonical middle) (lift_events es)) = es"
    by (rule Cons.IH[OF rest])
  show ?case using first tail
    by (simp add: lift_events_def run_state_append run_trace_append)
qed

definition planner_language :: "event list set" where
  "planner_language = {es. \<exists>r. ref_run (abstract_state initial) es = Some r}"

definition runtime_language :: "event list set" where
  "runtime_language = range (run_trace step initial)"

theorem controlled_language_equality:
  "project control_alphabet runtime_language = planner_language"
proof (rule equalityI)
  show "project control_alphabet runtime_language \<subseteq> planner_language"
    using runtime_refinement
    by (auto simp: project_def control_alphabet_def runtime_language_def planner_language_def)
  show "planner_language \<subseteq> project control_alphabet runtime_language"
  proof
    fix es assume "es \<in> planner_language"
    then obtain r where run: "ref_run (abstract_state initial) es = Some r"
      by (auto simp: planner_language_def)
    have lift: "filter controlled (run_trace step (canonical (abstract_state initial)) (lift_events es)) = es"
      using reference_lifting[OF run] by blast
    have "canonical (abstract_state initial) = initial"
      by (simp add: canonical_def abstract_state_def initial_def)
    with lift have eq: "filter controlled (run_trace step initial (lift_events es)) = es"
      by simp
    have "filter controlled (run_trace step initial (lift_events es)) \<in>
      project control_alphabet runtime_language"
      by (auto simp: project_def control_alphabet_def runtime_language_def)
    then show "es \<in> project control_alphabet runtime_language" using eq by simp
  qed
qed

text \<open>The hidden language below includes protocol bookkeeping as well as
advice events. It is an over-approximation, not an independently implemented
LLM process. The following connection proves the selector premise for the
operational protocol; it is not asserted as a projection axiom.\<close>

definition hidden_language :: "event list set" where
  "hidden_language = {es. \<forall>e\<in>set es. \<not> controlled e}"

lemma split_interleaves:
  "interleaves (filter controlled es) (filter (\<lambda>e. \<not> controlled e) es) es"
  by (induction es) (auto intro: interleaves.intros)

theorem operational_shuffle_embedding:
  "runtime_language \<subseteq> trace_parallel planner_language hidden_language"
proof
  fix es assume rt: "es \<in> runtime_language"
  have left: "filter controlled es \<in> planner_language"
    using rt controlled_language_equality
    by (auto simp: project_def control_alphabet_def)
  have right: "filter (\<lambda>e. \<not> controlled e) es \<in> hidden_language"
    by (auto simp: hidden_language_def)
  show "es \<in> trace_parallel planner_language hidden_language"
    unfolding trace_parallel_def
    using left right split_interleaves[of es] by blast
qed

definition select_runtime :: "event list set \<Rightarrow> event list set" where
  "select_runtime X = X \<inter> runtime_language"

lemma selector_represents_runtime:
  "select_runtime (trace_parallel planner_language hidden_language) = runtime_language"
  using operational_shuffle_embedding by (auto simp: select_runtime_def)

theorem cka_interface_boundary:
  "project control_alphabet
    (select_runtime (trace_parallel planner_language hidden_language)) \<subseteq>
      project control_alphabet planner_language"
proof (rule authority_boundary_traces)
  show "\<forall>ys\<in>hidden_language. filter (\<lambda>e. e \<in> control_alphabet) ys = []"
    by (auto simp: hidden_language_def control_alphabet_def filter_empty_conv)
  show "select_runtime (trace_parallel planner_language hidden_language) \<subseteq>
      trace_parallel planner_language hidden_language"
    by (auto simp: select_runtime_def)
qed

corollary actual_runtime_cka_bound:
  "project control_alphabet runtime_language \<subseteq> project control_alphabet planner_language"
  using cka_interface_boundary selector_represents_runtime by simp

lemma plain_planner_trace_requires_bookkeeping:
  "[Commit] \<in> planner_language"
  "[Commit] \<notin> runtime_language"
proof -
  show "[Commit] \<in> planner_language"
    by (auto simp: planner_language_def abstract_state_def initial_def)
  show "[Commit] \<notin> runtime_language"
  proof
    assume "[Commit] \<in> runtime_language"
    then obtain cs where eq: "run_trace step initial cs = [Commit]"
      by (auto simp: runtime_language_def)
    then obtain c rest where "cs = c # rest" by (cases cs) auto
    with eq have "snd (step initial c) = Commit" by simp
    then show False by (cases c) (auto simp: initial_def)
  qed
qed

lemma reference_at_most_once:
  assumes "ref_run r es = Some r'"
  shows "count_list es Commit \<le> (if snd r then 0 else 1)"
  using assms
proof (induction es arbitrary: r r')
  case Nil
  then show ?case by simp
next
  case (Cons e es)
  then obtain middle where one: "ref_step r e = Some middle"
    and rest: "ref_run middle es = Some r'"
    by (auto split: option.splits)
  have tail: "count_list es Commit \<le> (if snd middle then 0 else 1)"
    by (rule Cons.IH[OF rest])
  show ?case using one tail
    by (cases e; cases r) (auto split: if_splits)
qed

lemma count_commit_projection:
  "count_list (filter controlled es) Commit = count_list es Commit"
  by (induction es) (auto split: event.splits)

theorem runtime_at_most_once:
  "count_list (run_trace step initial cs) Commit \<le> 1"
  using reference_at_most_once[OF runtime_refinement[where s=initial and cs=cs]]
  by (simp add: count_commit_projection abstract_state_def initial_def)

fun work_left :: "phase \<Rightarrow> nat" where
  "work_left Idle = 3"
| "work_left Pending = 2"
| "work_left Approved = 1"
| "work_left Completed = 0"

lemma zero_work_completed:
  "work_left p = 0 \<longleftrightarrow> p = Completed"
  by (cases p) auto

lemma service_rank_step:
  assumes "permitted s" "stage s \<noteq> Idle" "c \<noteq> SetPermission False"
  shows "permitted (fst (step s c)) \<and> stage (fst (step s c)) \<noteq> Idle \<and>
    work_left (stage (fst (step s c))) = work_left (stage s) - (if c = Service then 1 else 0)"
  using assms by (cases "stage s"; cases c) auto

theorem service_rank_execution:
  assumes "permitted s" "stage s \<noteq> Idle" "SetPermission False \<notin> set cs"
  shows "permitted (run_state step s cs) \<and> stage (run_state step s cs) \<noteq> Idle \<and>
    work_left (stage (run_state step s cs)) = work_left (stage s) - count_list cs Service"
  using assms
proof (induction cs arbitrary: s)
  case Nil
  then show ?case by simp
next
  case (Cons c cs)
  have one: "permitted (fst (step s c)) \<and> stage (fst (step s c)) \<noteq> Idle \<and>
    work_left (stage (fst (step s c))) = work_left (stage s) - (if c = Service then 1 else 0)"
    using Cons.prems by (intro service_rank_step) auto
  have tail: "permitted (run_state step (fst (step s c)) cs) \<and>
    stage (run_state step (fst (step s c)) cs) \<noteq> Idle \<and>
    work_left (stage (run_state step (fst (step s c)) cs)) =
      work_left (stage (fst (step s c))) - count_list cs Service"
    using one Cons.prems by (intro Cons.IH) auto
  show ?case using one tail by (auto simp: diff_diff_left)
qed

theorem two_service_steps_suffice:
  assumes "permitted s" "stage s = Pending"
    "SetPermission False \<notin> set cs" "2 \<le> count_list cs Service"
  shows "stage (run_state step s cs) = Completed"
proof -
  have "work_left (stage (run_state step s cs)) = 2 - count_list cs Service"
    using service_rank_execution[of s cs] assms by auto
  then show ?thesis using assms zero_work_completed by auto
qed

theorem eventual_completion_with_service_supply:
  assumes permission: "permitted s" and pending: "stage s = Pending"
    and stable: "\<forall>n. inputs n \<noteq> SetPermission False"
    and supplied: "\<forall>k. \<exists>n. k \<le> count_list (map inputs [0..<n]) Service"
  shows "\<exists>n. stage (run_state step s (map inputs [0..<n])) = Completed"
proof -
  obtain n where enough: "2 \<le> count_list (map inputs [0..<n]) Service"
    using supplied by blast
  have quiet: "SetPermission False \<notin> set (map inputs [0..<n])"
    using stable by auto
  have "stage (run_state step s (map inputs [0..<n])) = Completed"
    using permission pending quiet enough by (rule two_service_steps_suffice)
  then show ?thesis by blast
qed

lemma completed_persists:
  "stage s = Completed \<Longrightarrow> stage (run_state step s cs) = Completed"
proof (induction cs arbitrary: s)
  case Nil
  then show ?case by simp
next
  case (Cons c cs)
  then show ?case by (cases c) auto
qed

text \<open>The progress bound counts trusted service steps, not elapsed time.
Arbitrary advice messages, lost acknowledgements and polling may occur between
them. Without service scheduling or with permission revoked, completion is not
promised. Equality above is a finite-language result, separate from this bound.\<close>

fun cached_step :: "istate \<Rightarrow> command \<Rightarrow> istate \<times> event" where
  "cached_step s Service = (if stage s = Approved then
      (s\<lparr>stage := Completed\<rparr>, Commit) else step s Service)"
| "cached_step s c = step s c"

fun advice_blocked_step :: "istate \<Rightarrow> command \<Rightarrow> istate \<times> event" where
  "advice_blocked_step s Service = (if stage s = Approved \<and> \<not> advice_available s then
      (s, Hidden Service) else step s Service)"
| "advice_blocked_step s c = step s c"

fun retry_step :: "istate \<Rightarrow> command \<Rightarrow> istate \<times> event" where
  "retry_step s LostAck =
    (s\<lparr>stage := (if stage s = Completed then Approved else stage s)\<rparr>, Hidden LostAck)"
| "retry_step s c = step s c"

lemma stale_permission_rejected:
  "filter controlled (run_trace step initial [Submit, Service, SetPermission False, Service]) = [Policy False]"
  by (simp add: initial_def)

lemma cached_permission_counterexample:
  "ref_run (abstract_state initial)
     (filter controlled (run_trace cached_step initial [Submit, Service, SetPermission False, Service])) = None"
  by (simp add: initial_def abstract_state_def)

lemma lost_ack_retry_safe:
  "filter controlled (run_trace step initial [Submit, Service, Service, LostAck, Submit, Service]) = [Commit]"
  by (simp add: initial_def)

lemma retry_counterexample:
  "filter controlled (run_trace retry_step initial [Submit, Service, Service, LostAck, Submit, Service]) = [Commit, Commit]"
  by (simp add: initial_def)

lemma advice_loss_does_not_block:
  "stage (run_state step initial [Submit, Service, Advice False, Service]) = Completed"
  by (simp add: initial_def)

lemma advice_dependency_blocks:
  "stage (run_state advice_blocked_step initial [Submit, Service, Advice False, Service]) = Approved"
  by (simp add: initial_def)

lemma permanent_advice_outage_blocks:
  "stage (run_state advice_blocked_step initial
    ([Submit, Service, Advice False] @ replicate n Service)) = Approved"
proof -
  have loop: "\<And>s. stage s = Approved \<Longrightarrow> \<not> advice_available s \<Longrightarrow>
      run_state advice_blocked_step s (replicate n Service) = s"
    by (induction n) auto
  show ?thesis by (simp add: initial_def run_state_append loop)
qed

definition make_state :: "bool \<Rightarrow> phase \<Rightarrow> bool \<Rightarrow> istate" where
  "make_state permission phase available =
    \<lparr>permitted = permission, stage = phase, advice_available = available\<rparr>"

ML \<open>
  val checked = @{thms step_simulation runtime_refinement reference_lifting
    controlled_language_equality operational_shuffle_embedding selector_represents_runtime
    cka_interface_boundary actual_runtime_cka_bound plain_planner_trace_requires_bookkeeping
    runtime_at_most_once service_rank_execution
    two_service_steps_suffice eventual_completion_with_service_supply completed_persists
    stale_permission_rejected cached_permission_counterexample
    lost_ack_retry_safe retry_counterexample advice_loss_does_not_block advice_dependency_blocks
    permanent_advice_outage_blocks};
  val _ = if Thm_Deps.has_skip_proof checked then error "Admitted runtime dependency" else ();
  val _ = if null (Thm_Deps.all_oracles checked)
    then Output.physical_stdout "AUDIT: runtime interface results have no oracle dependencies\n"
    else error "Oracle dependency in runtime results";
\<close>

export_code step initial run_state run_trace cached_step advice_blocked_step retry_step
  make_state permitted stage advice_available
  Submit Service SetPermission Advice LostAck Poll Policy Commit Hidden
  Idle Pending Approved Completed
  checking SML

export_code step initial run_state run_trace cached_step advice_blocked_step retry_step
  make_state permitted stage advice_available
  Submit Service SetPermission Advice LostAck Poll Policy Commit Hidden
  Idle Pending Approved Completed
  in SML module_name Runtime_Interface file_prefix runtime_interface

end
