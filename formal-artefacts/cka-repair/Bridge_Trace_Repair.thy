theory Bridge_Trace_Repair
  imports Bridge_Algebra_Repair
begin

text \<open>Languages contain finite traces of arbitrary length. No prefix-closure,
state-machine correspondence, infinite-run semantics or CKA instance is assumed.
The guard selects traces; implementability of this selector is a separate task.\<close>

inductive interleaves :: "'e list \<Rightarrow> 'e list \<Rightarrow> 'e list \<Rightarrow> bool" where
  empty: "interleaves [] [] []"
| left: "interleaves xs ys zs \<Longrightarrow> interleaves (x # xs) ys (x # zs)"
| right: "interleaves xs ys zs \<Longrightarrow> interleaves xs (y # ys) (y # zs)"

definition trace_parallel :: "'e list set \<Rightarrow> 'e list set \<Rightarrow> 'e list set" where
  "trace_parallel P D = {zs. \<exists>xs\<in>P. \<exists>ys\<in>D. interleaves xs ys zs}"

definition project :: "'e set \<Rightarrow> 'e list set \<Rightarrow> 'e list set" where
  "project C X = filter (\<lambda>e. e \<in> C) ` X"

definition trace_seq :: "'e list set \<Rightarrow> 'e list set \<Rightarrow> 'e list set" where
  "trace_seq X Y = {zs. \<exists>xs\<in>X. \<exists>ys\<in>Y. zs = xs @ ys}"

lemma trace_zero_and_unit:
  "trace_seq X {} = {}"
  "trace_seq X {[]} = X"
  "project C {} = {}"
  "project C {[]} = {[]}"
  by (auto simp: trace_seq_def project_def)

lemma subidentity_languages:
  "T \<subseteq> {[]} \<longleftrightarrow> T = {} \<or> T = {[]}"
  by blast

lemma project_mono:
  "X \<subseteq> Y \<Longrightarrow> project C X \<subseteq> project C Y"
  by (auto simp: project_def)

lemma interleaves_projection:
  assumes "interleaves xs ys zs"
      and "filter (\<lambda>e. e \<in> C) ys = []"
  shows "filter (\<lambda>e. e \<in> C) zs = filter (\<lambda>e. e \<in> C) xs"
  using assms by (induction rule: interleaves.induct) auto

lemma interleaves_right_empty:
  "interleaves xs [] xs"
  by (induction xs) (auto intro: interleaves.intros)

lemma planner_is_available:
  assumes "[] \<in> D"
  shows "P \<subseteq> trace_parallel P D"
  using assms interleaves_right_empty by (auto simp: trace_parallel_def)

theorem authority_boundary_traces:
  assumes silent: "\<forall>ys\<in>D. filter (\<lambda>e. e \<in> C) ys = []"
      and guard: "G (trace_parallel P D) \<subseteq> trace_parallel P D"
  shows "project C (G (trace_parallel P D)) \<subseteq> project C P"
proof -
  have "project C (trace_parallel P D) \<subseteq> project C P"
  proof
    fix zs
    assume "zs \<in> project C (trace_parallel P D)"
    then obtain xs ys ws where
      xs: "xs \<in> P" and ys: "ys \<in> D"
      and mix: "interleaves xs ys ws"
      and zs: "zs = filter (\<lambda>e. e \<in> C) ws"
      by (auto simp: project_def trace_parallel_def)
    have "filter (\<lambda>e. e \<in> C) ys = []"
      using silent ys by blast
    then have "filter (\<lambda>e. e \<in> C) ws = filter (\<lambda>e. e \<in> C) xs"
      by (rule interleaves_projection[OF mix])
    then show "zs \<in> project C P"
      using xs zs by (auto simp: project_def)
  qed
  moreover have "project C (G (trace_parallel P D)) \<subseteq> project C (trace_parallel P D)"
    using guard by (rule project_mono)
  ultimately show ?thesis by blast
qed

text \<open>Retention is a separate premise about the guard. The next equality is
not a theorem that every contracting guard retains useful planner behaviour.\<close>

theorem authority_equality_with_retention:
  assumes silent: "\<forall>ys\<in>D. filter (\<lambda>e. e \<in> C) ys = []"
      and guard: "G (trace_parallel P D) \<subseteq> trace_parallel P D"
      and retained: "P \<subseteq> G (trace_parallel P D)"
  shows "project C (G (trace_parallel P D)) = project C P"
  using authority_boundary_traces[where G=G and P=P and D=D and C=C, OF silent guard]
    project_mono[OF retained, where C=C]
  by blast

corollary represented_completion_retained:
  assumes silent: "\<forall>ys\<in>D. filter (\<lambda>e. e \<in> C) ys = []"
      and guard: "G (trace_parallel P D) \<subseteq> trace_parallel P D"
      and retained: "P \<subseteq> G (trace_parallel P D)"
  shows "(\<exists>zs\<in>project C (G (trace_parallel P D)). completes zs)
    \<longleftrightarrow> (\<exists>xs\<in>project C P. completes xs)"
  using authority_equality_with_retention[where G=G and P=P and D=D and C=C,
    OF silent guard retained] by simp

text \<open>The following finite witnesses show that the two boundary premises
matter. Unit is kept distinct from zero; blocking all nonempty prefixes retains
the empty trace and can lose a completing trace while satisfying inclusion.\<close>

lemma controlled_advice_counterexample:
  "\<not> project {True} (trace_parallel {[]} {[True]}) \<subseteq> project {True} {[]}"
proof -
  have "interleaves [] [True] [True]"
    by (auto intro: interleaves.intros)
  then show ?thesis by (auto simp: project_def trace_parallel_def)
qed

lemma guard_injection_counterexample:
  "\<not> project {True} {[True]} \<subseteq> project {True} {[]}"
  by (auto simp: project_def)

lemma block_all_nonempty_prefixes:
  "project {True} {[]} \<subseteq> project {True} {[], [True]}"
  "[] \<in> project {True} {[]}"
  "[True] \<notin> project {True} {[]}"
  "[True] \<in> project {True} {[], [True]}"
  by (auto simp: project_def)

ML \<open>
  val checked = @{thms trace_zero_and_unit subidentity_languages project_mono
    interleaves_projection interleaves_right_empty planner_is_available
    authority_boundary_traces authority_equality_with_retention
    represented_completion_retained controlled_advice_counterexample
    guard_injection_counterexample block_all_nonempty_prefixes};
  val _ = if Thm_Deps.has_skip_proof checked
    then error "Admitted dependency in trace results" else ();
  val _ = if null (Thm_Deps.all_oracles checked)
    then Output.physical_stdout "AUDIT: trace results have no oracle dependencies\n"
    else error "Oracle dependency in trace results";
\<close>

end
