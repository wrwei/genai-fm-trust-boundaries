theory AMR_Progress
  imports Complex_Main
begin

text \<open>The exact rest-to-rest profile has peak w, cruise distance c, and
k = 1/(2*a) + 1/(2*b). Its duration is 2*k*w+c/w and length k*w^2+c.
The premises describe exact positive dynamics; acceleration upper bounds alone
do not discharge them.\<close>

lemma triangular_time_bound:
  fixes k v w :: real
  assumes "0 < v" "0 \<le> k"
  shows "2*k*w \<le> k*w^2/v + k*v"
proof -
  have nonneg: "0 \<le> k*(v-w)^2/v" using assms
    by (simp add:mult_nonneg_nonneg divide_nonneg_pos)
  have eq: "k*w^2/v+k*v-2*k*w=k*(v-w)^2/v"
    using assms by (simp add:field_simps power2_eq_square algebra_simps)
  show ?thesis using nonneg eq by linarith
qed

theorem profile_time_bound:
  fixes k v w c L :: real
  assumes "0 < v" "0 < w" "0 \<le> k" "0 \<le> c" "w \<le> v"
      and "c=0 \<or> w=v" "L=k*w^2+c"
  shows "2*k*w+c/w \<le> L/v+k*v"
  using assms triangular_time_bound[of v k w]
  by (cases "c=0") (auto simp:field_simps power2_eq_square)

lemma positive_profile_coefficient:
  fixes a b :: real
  assumes "0<a" "0<b"
  shows "0 < 1/(2*a)+1/(2*b)"
  using assms by (intro add_pos_pos; simp)

lemma min_peak_conditions:
  fixes L k v w c :: real
  assumes "0<L" "0<k" "0<v"
  defines "w \<equiv> min v (sqrt (L/k))" and "c \<equiv> L-k*w^2"
  shows "0<w" "0\<le>c" "w\<le>v" "c=0 \<or> w=v" "L=k*w^2+c"
proof -
  have pos: "0 < L/k" using assms by simp
  have root: "sqrt (L/k)^2=L/k" using pos by simp
  have scale: "k*(L/k)=L" using assms by simp
  show "0<w" using assms pos by (simp add:w_def)
  have sq: "(min v (sqrt (L/k)))^2 \<le> (sqrt (L/k))^2"
    using assms pos by (intro power_mono; simp)
  have "k*(min v (sqrt (L/k)))^2 \<le> k*(sqrt (L/k))^2"
    using sq assms by (intro mult_left_mono) auto
  then show "0\<le>c" using root scale by (simp add:w_def c_def)
  show "w\<le>v" by (simp add:w_def)
  show "c=0 \<or> w=v" using root scale by (auto simp:w_def c_def min_def)
  show "L=k*w^2+c" by (simp add:c_def)
qed

corollary planned_segment_time_bound:
  fixes L k v w :: real
  assumes "0<L" "0<k" "0<v"
  defines "w \<equiv> min v (sqrt (L/k))"
  shows "2*k*w+(L-k*w^2)/w \<le> L/v+k*v"
  using profile_time_bound[of v w k "L-k*w^2" L]
        min_peak_conditions[OF assms(1-3)] assms
  by (auto simp:w_def)

fun drain :: "real \<Rightarrow> real list \<Rightarrow> real list" where
  "drain t []=[]"
| "drain t (d#ds)=(if d\<le>t then drain (t-d) ds else (d-t)#ds)"

theorem finite_schedule_drains:
  assumes "\<forall>d\<in>set ds. 0\<le>d" "sum_list ds\<le>t"
  shows "drain t ds=[]"
  using assms
proof (induction ds arbitrary:t)
  case Nil then show ?case by simp
next
  case (Cons d ds)
  have "0 \<le> sum_list ds" using Cons.prems by (auto intro:sum_list_nonneg)
  with Cons show ?case by (simp; linarith)
qed

lemma schedule_budget:
  fixes ds bs :: "real list"
  assumes "list_all2 (\<le>) ds bs"
  shows "sum_list ds \<le> sum_list bs"
  using assms by induction auto

text \<open>Only accounting: these timestamp inequalities are obligations, not
conclusions about the Python driver. Both tasks' local start/travel/finish bounds
must first be discharged. The second can be granted before the first finishes.\<close>
theorem two_task_budget:
  fixes G S P F g1 s1 a1 f1 g2 s2 a2 f2 :: real
  assumes "0\<le>G" "0\<le>S" "0\<le>P" "0\<le>F"
      and "g1\<le>G" "s1\<le>g1+S" "a1\<le>s1+P" "f1\<le>a1+F"
      and "g2\<le>f1+G" "s2\<le>g2+S" "a2\<le>s2+P" "f2\<le>a2+F"
  shows "max f1 f2 \<le> 2*(G+S+P+F)"
  using assms by (simp add:max_def; linarith)

lemma nominal_budget: "2*((1/10::real)+2+31+2)=351/5" by simp

text \<open>A full kinematically consistent countermodel: x'=v=0, v'=a=0.
An upper speed and acceleration envelope permits it forever. No premise about
receiving Proceed connects that command to positive acceleration in that envelope.\<close>
theorem upper_bounds_do_not_imply_completion:
  fixes A V x0 goal :: real
  assumes "0\<le>A" "0\<le>V" "x0\<noteq>goal"
  shows "\<exists>x v a :: real \<Rightarrow> real.
    x 0=x0 \<and> (\<forall>t. (x has_real_derivative v t) (at t) \<and>
      (v has_real_derivative a t) (at t) \<and>
      0\<le>v t \<and> v t\<le>V \<and> 0\<le>a t \<and> a t\<le>A \<and> x t\<noteq>goal)"
  apply (rule exI[where x="\<lambda>_::real. x0"])
  apply (rule exI[where x="\<lambda>_::real. (0::real)"])
  apply (rule exI[where x="\<lambda>_::real. (0::real)"])
  using assms by simp

ML \<open>
 val checked = @{thms triangular_time_bound profile_time_bound positive_profile_coefficient
   min_peak_conditions planned_segment_time_bound finite_schedule_drains schedule_budget
   two_task_budget nominal_budget upper_bounds_do_not_imply_completion};
 val _ = if Thm_Deps.has_skip_proof checked then error "Admitted dependency" else ();
 val _ = if null (Thm_Deps.all_oracles checked) then () else error "Oracle dependency";
 val audit = "No skipped proofs or oracle dependencies\n" ^ cat_lines (map (fn th => Thm_Name.print (Thm.get_name_hint th)) checked);
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "progress-audit.txt")) [XML.Text audit];
\<close>
end
