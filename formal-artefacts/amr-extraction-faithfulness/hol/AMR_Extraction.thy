theory AMR_Extraction
  imports Main
begin

text \<open>Pure Boolean expressions and total environments. The HOL stack stores the
top at the head (the reverse of the Python list representation). Source rules
use first-match semantics; target rules expose all enabled outcomes.\<close>
datatype expr = Lit bool | Atom nat | BNot expr | BAnd "expr list" | BOr "expr list"
datatype insn = Push bool | Load nat | Neg | Conj nat | Disj nat

primrec eval_expr :: "(nat \<Rightarrow> bool) \<Rightarrow> expr \<Rightarrow> bool" where
 "eval_expr env (Lit b)=b"
| "eval_expr env (Atom a)=env a"
| "eval_expr env (BNot e)=(\<not> eval_expr env e)"
| "eval_expr env (BAnd es)=list_all id (map (eval_expr env) es)"
| "eval_expr env (BOr es)=list_ex id (map (eval_expr env) es)"

fun instruction :: "(nat \<Rightarrow> bool) \<Rightarrow> insn \<Rightarrow> bool list \<Rightarrow> bool list option" where
 "instruction env (Push b) st=Some (b#st)"
| "instruction env (Load a) st=Some (env a#st)"
| "instruction env Neg []=None"
| "instruction env Neg (b#st)=Some ((\<not>b)#st)"
| "instruction env (Conj n) st=(if n\<le>length st then Some (list_all id (take n st)#drop n st) else None)"
| "instruction env (Disj n) st=(if n\<le>length st then Some (list_ex id (take n st)#drop n st) else None)"

fun run_code where
 "run_code [] env st=Some st"
| "run_code (i#is) env st=(case instruction env i st of None \<Rightarrow> None | Some t \<Rightarrow> run_code is env t)"

lemma run_append:
 "run_code (xs@ys) env st=(case run_code xs env st of None \<Rightarrow> None | Some t \<Rightarrow> run_code ys env t)"
 by (induction xs arbitrary:st) (auto split:option.splits)

definition negate where
 "negate code=(if code\<noteq>[] \<and> last code=Neg then butlast code else code@[Neg])"

lemma instruction_neg_inverse:
 "instruction env Neg st=Some (b#rest) \<Longrightarrow> st=(\<not>b)#rest"
 by (cases st) auto

lemma negate_correct:
 assumes "run_code code env st=Some (b#rest)"
 shows "run_code (negate code) env st=Some ((\<not>b)#rest)"
 using assms
 by (cases code rule:rev_cases)
    (auto simp:negate_def run_append dest:instruction_neg_inverse split:insn.splits option.splits list.splits)

primrec compile where
 "compile (Lit b)=[Push b]"
| "compile (Atom a)=[Load a]"
| "compile (BNot e)=negate (compile e)"
| "compile (BAnd es)=concat (map compile es) @ [Conj (length es)]"
| "compile (BOr es)=concat (map compile es) @ [Disj (length es)]"

lemma run_concat:
 assumes "\<forall>e\<in>set es. \<forall>st. run_code (f e) env st=Some (g e#st)"
 shows "run_code (concat (map f es)) env st=Some (rev (map g es) @ st)"
 using assms
 by (induction es arbitrary:st) (auto simp:run_append)

theorem compile_correct:
 "run_code (compile e) env st=Some (eval_expr env e#st)"
proof (induction e arbitrary:st)
 case (Lit b) then show ?case by simp
next
 case (Atom a) then show ?case by simp
next
 case (BNot e) then show ?case using negate_correct by simp
next
 case (BAnd es)
 have run: "run_code (concat (map compile es)) env st=Some (rev (map (eval_expr env) es) @ st)"
   by (rule run_concat) (use BAnd.IH in auto)
 show ?case by (simp add:run_append run list_all_iff)
next
 case (BOr es)
 have run: "run_code (concat (map compile es)) env st=Some (rev (map (eval_expr env) es) @ st)"
   by (rule run_concat) (use BOr.IH in auto)
 show ?case by (simp add:run_append run list_ex_iff)
qed

text \<open>Each preceding raw condition is negated, exactly as in _extract_rules.
These appended NOT instructions are not the optimizing negate function.\<close>
fun priority where
 "priority [] code=code"
| "priority (p#ps) code=priority ps (code @ compile p @ [Neg,Conj 2])"

lemma priority_correct:
 assumes "run_code code env st=Some (b#st)"
 shows "run_code (priority ps code) env st=Some ((b \<and> (\<forall>p\<in>set ps. \<not> eval_expr env p))#st)"
 using assms
 by (induction ps arbitrary:code b) (auto simp:run_append compile_correct)

fun source_result :: "(nat \<Rightarrow> bool) \<Rightarrow> (expr \<times> 'a) list \<Rightarrow> 'a option" where
 "source_result env []=None"
| "source_result env ((e,a)#rs)=(if eval_expr env e then Some a else source_result env rs)"

fun extract_aux :: "expr list \<Rightarrow> (expr \<times> 'a) list \<Rightarrow> (insn list \<times> 'a) list" where
 "extract_aux ps []=[]"
| "extract_aux ps ((e,a)#rs)=(priority ps (compile e),a)#extract_aux (ps@[e]) rs"
definition extract_rules where "extract_rules rs=extract_aux [] rs"
definition enabled where "enabled env code=(run_code code env []=Some [True])"
fun target_results :: "(nat \<Rightarrow> bool) \<Rightarrow> (insn list \<times> 'a) list \<Rightarrow> 'a list" where
 "target_results env []=[]"
| "target_results env ((code,a)#rs)=(if enabled env code then [a] else []) @ target_results env rs"
fun result_list where "result_list None=[]" | "result_list (Some a)=[a]"

lemma priority_enabled:
 "enabled env (priority ps (compile e))=(eval_expr env e \<and> (\<forall>p\<in>set ps. \<not>eval_expr env p))"
 using priority_correct[OF compile_correct,of ps] by (auto simp:enabled_def)

lemma extraction_with_prefix:
 "target_results env (extract_aux ps rs)=(if (\<forall>p\<in>set ps. \<not>eval_expr env p)
   then result_list (source_result env rs) else [])"
 by (induction rs arbitrary:ps) (auto simp:priority_enabled split:prod.splits)

theorem extraction_preserves:
 "target_results env (extract_rules rs)=result_list (source_result env rs)"
 by (simp add:extract_rules_def extraction_with_prefix)

corollary target_singleton_iff:
 "target_results env (extract_rules rs)=[a] \<longleftrightarrow> source_result env rs=Some a"
 by (cases "source_result env rs") (simp_all add:extraction_preserves)
corollary no_match_preserved:
 "target_results env (extract_rules rs)=[] \<longleftrightarrow> source_result env rs=None"
 by (cases "source_result env rs") (simp_all add:extraction_preserves)
corollary property_lifting:
 "source_result env rs=Some a \<Longrightarrow>
   (\<forall>b\<in>set (target_results env (extract_rules rs)). Q b) \<Longrightarrow> Q a"
 by (simp add:extraction_preserves)

corollary total_property_lifting:
 "target_results env (extract_rules rs)\<noteq>[] \<Longrightarrow>
   (\<forall>b\<in>set (target_results env (extract_rules rs)). Q b) \<Longrightarrow>
   \<exists>a. source_result env rs=Some a \<and> Q a"
 by (cases "source_result env rs") (simp_all add:extraction_preserves)

corollary compile_nonempty: "compile e\<noteq>[]"
 using compile_correct[of e "\<lambda>_. False" "[]"] by auto

text \<open>Constructed witnesses, not observed model-generation failures.\<close>
lemma omitted_priority_witness:
 "source_result env [(Lit True,0::nat),(Lit True,1)]=Some 0"
 "target_results env [(compile (Lit True),0::nat),(compile (Lit True),1)]=[0,1]"
 by (simp_all add:enabled_def)
lemma incorrect_negation_witness:
 "eval_expr env (BNot (Lit True))=False"
 "run_code (compile (Lit True)) env []=Some [True]"
 by simp_all
lemma uncovered_witness:
 "source_result env [(Lit False,0::nat)]=None"
 "target_results env (extract_rules [(Lit False,0::nat)])=[]"
 by (simp_all add:extraction_preserves)

ML \<open>
 val checked = @{thms negate_correct compile_correct priority_correct extraction_preserves
 target_singleton_iff no_match_preserved property_lifting total_property_lifting compile_nonempty omitted_priority_witness
 incorrect_negation_witness uncovered_witness};
 val _ = if Thm_Deps.has_skip_proof checked then error "Admitted dependency" else ();
 val _ = if null (Thm_Deps.all_oracles checked) then () else error "Oracle dependency";
 val audit = "No skipped proofs or oracle dependencies\n" ^ cat_lines (map (fn th => Thm_Name.print (Thm.get_name_hint th)) checked);
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "proof-audit.txt")) [XML.Text audit];
\<close>
end
