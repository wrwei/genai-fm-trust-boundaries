theory AMR_Runtime_Binding
  imports "AMR_Advisory_V2.AMR_Protocol"
begin

text \<open>Wire parameters are equality classes and parsing outcomes, not a proof of JSON parsing.
One serial fixed-mission instance: no cancellation, identity reuse or concurrent callbacks.\<close>
datatype raw_input = Wire bool bool "robot option" | Reg robot | Obs bool bool
  | Choose | Serve | CommitNow | Send robot | ApplyNow | Clear robot bool | Open | Read

fun selected where
 "selected (s,m) = (if pending s=None then select s (slot m) else None)"
fun local_input where
 "local_input sm (Reg r)=Register r"
| "local_input sm (Obs b f)=Observe b f"
| "local_input sm Choose=Validate (selected sm)"
| "local_input sm Serve=Service (selected sm)"
| "local_input sm CommitNow=Commit"
| "local_input sm (Send r)=Issue r"
| "local_input sm ApplyNow=Apply"
| "local_input sm (Clear r b)=Release r b"
| "local_input sm Open=RequestAdvice"
| "local_input sm Read=Consume (slot (snd sm))"
| "local_input sm (Wire a b r)=RequestAdvice"

fun raw_event where
 "raw_event sm (Wire a b r)=Provider (if a \<and> b then r else None)"
| "raw_event sm x=Trusted (local_input sm x) (snd (step (fst sm) (local_input sm x)))"

fun raw_step :: "core \<times> mailbox \<Rightarrow> raw_input \<Rightarrow> core \<times> mailbox" where
 "raw_step (s,m) (Wire a b r)=(s,if a \<and> b \<and> registered m \<and> slot m=None \<and> r\<noteq>None
   then m\<lparr>slot:=r\<rparr> else m)"
| "raw_step (s,m) Open=(s,m\<lparr>registered:=True\<rparr>)"
| "raw_step (s,m) x=(fst (step s (local_input (s,m) x)),m)"

lemma adapter_step_correspondence:
 "source_next sm (raw_event sm x)=Some (raw_step sm x)"
 by (cases sm; cases x)
    (auto simp:source_next_def split:if_splits)

fun raw_events where
 "raw_events sm []=[]"
| "raw_events sm (x#xs)=raw_event sm x # raw_events (raw_step sm x) xs"
fun raw_state where
 "raw_state sm []=sm"
| "raw_state sm (x#xs)=raw_state (raw_step sm x) xs"

theorem adapter_accepts:
 "accepts source_next sm (raw_events sm xs)"
 by (induction xs arbitrary:sm) (simp_all add:adapter_step_correspondence)

definition S_bound where
 "S_bound={raw_events (initial,m_initial) xs |xs. True}"
theorem adapter_source_inclusion: "S_bound \<subseteq> S_source"
 using adapter_accepts by (auto simp:S_bound_def S_source_def)
theorem adapter_component_embedding:
 "S_bound \<subseteq> G_T (trace_parallel P_open D)"
 using adapter_source_inclusion source_inclusion operational_embedding by blast
theorem adapter_authority: "project V S_bound \<subseteq> P_ref"
 using project_mono[OF adapter_source_inclusion] source_authority by blast

fun message_only where "message_only (Wire a b r)=True" | "message_only x=False"
lemma message_preserves_core:
 "message_only x \<Longrightarrow> fst (raw_step sm x)=fst sm"
 by (cases sm; cases x) auto
lemma messages_preserve_core:
 "\<forall>x\<in>set xs. message_only x \<Longrightarrow> fst (raw_state sm xs)=fst sm"
 by (induction xs arbitrary:sm) (auto simp:message_preserves_core)

lemma serve_core:
 "fst (raw_step (s,m) Serve)=fst (step s (Service (selected (s,m))))"
 by simp

text \<open>Authorization, not mission completion: two supplied service opportunities,
usable requests/permission initially, no permission-changing input between them.
Any finite number of arbitrary message inputs is allowed in that interval.\<close>
theorem adapter_two_service_authorization:
 assumes "pending s=None" "\<exists>r. legal s r"
   "\<forall>x\<in>set xs. message_only x"
 shows "\<exists>r. snd (step (fst (raw_state (raw_step (s,m) Serve) xs))
   (local_input (raw_state (raw_step (s,m) Serve) xs) Serve))=Some (Grant r)"
proof -
 obtain r where r: "select s (slot m)=Some r" "legal s r"
   using selector_total_legal[OF assms(2),of "slot m"] by blast
 have core: "fst (raw_state (raw_step (s,m) Serve) xs)=fst (step s (Service (Some r)))"
   using messages_preserve_core[OF assms(3),of "raw_step (s,m) Serve"] assms(1) r by simp
 show ?thesis using service_progress[OF assms(1) r(2)] core
   by (metis local_input.simps(4))
qed

definition all_mailboxes where
 "all_mailboxes=concat (map (\<lambda>b. map (\<lambda>r. \<lparr>registered=b,slot=r\<rparr>) opts) bools)"
definition all_raw where
 "all_raw=map Reg robots @ concat (map (\<lambda>b. map (Obs b) bools) bools) @
 [Choose,Serve,CommitNow] @ map Send robots @ [ApplyNow] @
 concat (map (\<lambda>r. map (Clear r) bools) robots) @ [Open,Read] @
 concat (map (\<lambda>a. concat (map (\<lambda>b. map (Wire a b) opts) bools)) bools)"
definition enc_sm where
 "enc_sm sm=enc_s (fst sm) @ [enc_b (registered (snd sm)),enc_r (slot (snd sm))]"
fun enc_i :: "input \<Rightarrow> integer list" where
 "enc_i (Register r)=[1,enc_r (Some r),0]"
| "enc_i (Observe b f)=[2,enc_b b,enc_b f]"
| "enc_i (Validate r)=[3,enc_r r,0]"
| "enc_i Commit=[4,0,0]"
| "enc_i (Issue r)=[5,enc_r (Some r),0]"
| "enc_i Apply=[6,0,0]"
| "enc_i (Release r b)=[7,enc_r (Some r),enc_b b]"
| "enc_i (Service r)=[8,enc_r r,0]"
| "enc_i RequestAdvice=[9,0,0]"
| "enc_i (Reply r)=[10,enc_r r,0]"
| "enc_i (Consume r)=[11,enc_r r,0]"
fun enc_e where
 "enc_e (Provider r)=[1,enc_r r,0,0,0,0,0]"
| "enc_e (Trusted i v)=[2] @ enc_i i @ enc_v v"
definition binding_rows where
 "binding_rows=concat (map (\<lambda>s. concat (map (\<lambda>m. map (\<lambda>x.
 enc_sm (s,m) @ enc_sm (raw_step (s,m) x) @ enc_e (raw_event (s,m) x)) all_raw) all_mailboxes)) all_states)"

ML \<open>
 val checked = @{thms adapter_step_correspondence adapter_accepts adapter_source_inclusion
 adapter_component_embedding adapter_authority messages_preserve_core adapter_two_service_authorization};
 val _ = if Thm_Deps.has_skip_proof checked then error "Admitted dependency" else ();
 val _ = if null (Thm_Deps.all_oracles checked) then () else error "Oracle dependency";
 val audit = "No skipped proofs or oracle dependencies\n" ^ cat_lines (map (fn th => Thm_Name.print (Thm.get_name_hint th)) checked);
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "binding-proof-audit.txt")) [XML.Text audit];
 val rows = @{code binding_rows};
 val _ = if length rows = 77760 then () else error "Unexpected finite domain";
 val body = cat_lines (map (space_implode "," o map IntInf.toString) rows);
 val _ = Export.export @{theory} (Path.binding0 (Path.explode "binding.csv")) [XML.Text body];
 val _ = writeln ("EXPORT: " ^ Int.toString (length rows) ^ " independently HOL-evaluated binding transitions");
\<close>
end
