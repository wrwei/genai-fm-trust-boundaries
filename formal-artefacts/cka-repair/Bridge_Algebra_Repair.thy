theory Bridge_Algebra_Repair
  imports Main
begin

text \<open>Independent repair session: no imports from the admitted legacy bridge
theories. HOL's dioid suffices for these two elementary facts; neither fact
requires additive idempotence, a parallel-composition law, or Kleene star.\<close>

lemma test_shrinks:
  fixes x t :: "'a::dioid"
  assumes "t \<le> 1"
  shows "x * t \<le> x"
proof -
  have "x * t \<le> x * 1"
    using assms by (intro mult_left_mono) auto
  then show ?thesis by simp
qed

lemma inequality_is_vacuous_for_zero:
  fixes P D :: "'a::dioid"
    and parallel :: "'a \<Rightarrow> 'a \<Rightarrow> 'a"
    and project :: "'a \<Rightarrow> 'b::order"
  assumes "mono project"
  shows "project (parallel P D * 0) \<le> project P"
proof -
  have "project 0 \<le> project P"
    using assms by (rule monoD) simp
  then show ?thesis by simp
qed

ML \<open>
  val checked = @{thms test_shrinks inequality_is_vacuous_for_zero};
  val _ = if Thm_Deps.has_skip_proof checked
    then error "Admitted dependency in foundational lemmas" else ();
  val _ = if null (Thm_Deps.all_oracles checked)
    then Output.physical_stdout "AUDIT: foundational lemmas have no oracle dependencies\n"
    else error "Oracle dependency in foundational lemmas";
\<close>

end
