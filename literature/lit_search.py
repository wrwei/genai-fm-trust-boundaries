"""Inspect the saved arXiv search snapshot or retrieve new unlabelled records.

python3 literature/lit_search.py --cached  # recount ORIGINAL saved labels
python3 literature/lit_search.py           # network retrieval, NOT classification

The saved 363-record snapshot is unchanged by either command. Original raw
retrieval responses, exclusions, classifier identity/settings and notebook are
not available. Thus the original search/classification cannot be fully rerun.
The taxonomy prompt below records the original rubric, including its conflation
of tests with model judgement. It is retained as provenance, not endorsed as a
validated taxonomy. See label_corrections.json for targeted source corrections
and check_counts.py for the corrected summary. No field prevalence is inferred.

Repair on 2026-09-09: regex boundaries had been double-escaped and matched no
saved records. Correcting the escapes matches all 363, but does not reconstruct
the original retrieval or establish eligibility. Live retrieval retains the
legacy cap of 1,000 records per query and has no historical date restriction;
it must not be described as an exact rerun of the snapshot search.
"""
import collections, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
import xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom"}

QUERIES = {'llm_formal_verification': 'abs:"large language model" AND abs:"formal verification"', 'llm_theorem_proving': 'abs:"large language model" AND (abs:"theorem proving" OR abs:"proof assistant")', 'llm_model_checking': 'abs:"large language model" AND abs:"model checking"', 'llm_specification': 'abs:"large language model" AND (abs:"formal specification" OR abs:"specification generation")', 'llm_invariant_contract': 'abs:"large language model" AND (abs:"loop invariant" OR abs:"program contract" OR abs:"postcondition")', 'llm_dafny_verifier': 'abs:"large language model" AND (abs:Dafny OR abs:"deductive verification" OR abs:"verification condition")', 'llm_isabelle_coq_lean': 'abs:"large language model" AND (abs:Isabelle OR abs:Coq OR abs:"Lean 4" OR abs:Lean)', 'llm_code_correctness': 'abs:"large language model" AND abs:"code generation" AND (abs:correctness OR abs:verified)', 'llm_repair_cegis': 'abs:"large language model" AND (abs:"counterexample" OR abs:"program repair") AND abs:verif', 'llm_runtime_monitor': 'abs:"large language model" AND (abs:"runtime verification" OR abs:"runtime monitor" OR abs:"shielding")', 'assurance_case_ml': 'abs:"assurance case" AND (abs:"machine learning" OR abs:"neural" OR abs:autonom)', 'llm_safety_critical': 'abs:"large language model" AND (abs:"safety-critical" OR abs:"safety case")', 'neurosymbolic_verif': 'abs:"neuro-symbolic" AND abs:verif', 'llm_agent_verification': 'abs:"LLM agent" AND (abs:verif OR abs:"formal")'}

GEN = re.compile(r'\b(large language model|LLM|LLMs|GPT-?[45o]|foundation model|code model|language model|transformer|generative (AI|model))\b', re.I)
FORMAL = re.compile(r'\b(formal verification|formally verif|theorem prover|proof assistant|model check|refinement (check|calculus)|Dafny|Isabelle|Coq|Lean\s?4|\bTLA\+|SMT solver|verification condition|loop invariant|postcondition|precondition|Hoare|separation logic|runtime verification|runtime monitor|assurance case|safety case|temporal logic|LTL|CTL|process algebra|CSP\b|symbolic execution|abstract interpretation|deductive verification|proof obligation|certified|proof script)\b', re.I)

TAXONOMY = 'You are classifying a paper for a survey on where LLM-plus-formal-methods work places its TRUST BOUNDARY.\n\nAssign exactly one PRIMARY class:\n\nA_GEN_CHECKED  = LLM drafts an artefact (code/spec/model); an INDEPENDENT formal tool\n                 decides accept/reject. The tool\'s verdict is the evidence.\nB_GEN_PROOF    = LLM drafts proofs/proof scripts/tactics for a proof assistant, which\n                 checks them. (Kernel is the discriminator; the target is a PROOF.)\nC_LLM_AS_ORACLE= The LLM itself judges correctness, or its output is trusted without an\n                 independent checker (LLM-as-judge, self-verification, self-consistency,\n                 confidence scores, benchmark pass@k with only tests).\nD_FORMAL_HELPS_LLM = Direction reversed: formal techniques used to improve/steer/analyse\n                 the model (verified decoding, constrained generation, formal analysis OF\n                 the network, guardrails synthesised for the model).\nE_RUNTIME      = The check happens at RUN TIME on a deployed system (runtime monitor,\n                 shield, enforcement, supervisory filter).\nF_ASSURANCE    = Assurance/safety cases, certification argument, regulatory evidence.\nG_OTHER        = None of the above, or off-topic for this survey.\n\nAlso answer:\n- artefact: what the LLM produces (code | spec | proof | model | invariant | test | plan | other | none)\n- checker: the deciding tool if named (dafny|isabelle|coq|lean|smt|model_checker|tests|none|other)\n- empirical: true if it reports a quantitative evaluation, false if position/survey/vision\n\nReply ONLY compact JSON:\n{"class":"A_GEN_CHECKED","artefact":"code","checker":"dafny","empirical":true}'


def arxiv(search_query, max_results=200, start=0):
    p = {"search_query": search_query, "start": start, "max_results": max_results,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(p)
    for a in range(4):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return ET.fromstring(r.read())
        except Exception:
            if a == 3:
                raise
            time.sleep(3 * (a + 1))


def parse(root):
    out = []
    for e in root.findall("a:entry", NS):
        out.append({
            "id": e.findtext("a:id", "", NS).rsplit("/", 1)[-1],
            "title": " ".join((e.findtext("a:title", "", NS) or "").split()),
            "abstract": " ".join((e.findtext("a:summary", "", NS) or "").split()),
            "date": (e.findtext("a:published", "", NS) or "")[:10],
            "authors": [a.findtext("a:name", "", NS) for a in e.findall("a:author", NS)],
            "cats": [c.get("term") for c in e.findall("a:category", NS)],
        })
    return out


def sweep():
    corpus = {}
    for name, q in QUERIES.items():
        got, start = [], 0
        while True:
            root = arxiv(q, 200, start)
            batch = parse(root)
            got += batch
            total = int(root.findtext(
                "{http://a9.com/-/spec/opensearch/1.1/}totalResults") or 0)
            start += len(batch)
            if not batch or start >= total or start >= 1000:
                break
            time.sleep(3)
        for r in got:
            base = r["id"].split("v")[0]
            rec = corpus.setdefault(base, r)          # insert first,
            rec["_q"] = sorted(set(rec.get("_q", [])) | {name})  # then mutate
        print(f"{name:26} total={total:5} corpus={len(corpus)}")
        time.sleep(3)
    return corpus


def on_topic(r):
    txt = r["title"] + " " + r["abstract"]
    return bool(GEN.search(txt)) and bool(FORMAL.search(txt))


if __name__ == "__main__":
    if "--cached" in sys.argv:
        labels = json.loads((HERE / "corpus_labelled.json").read_text())
        print("loaded", len(labels), "labelled papers from cache")
    else:
        corpus = sweep()
        core = {k: v for k, v in corpus.items() if on_topic(v)}
        print(f"\ncorpus {len(corpus)} -> on-topic {len(core)}")
        print("Classification needs host.llm(); run the notebook cell for that step.")
        json.dump(list(core.values()), (HERE / "corpus_core.json").open("w"), indent=1)
        raise SystemExit(0)

    cnt = collections.Counter(l["class"] for l in labels)
    print("\ntrust-boundary distribution:")
    for c, n in cnt.most_common():
        print(f"  {c:20} {n:4}  {100 * n / len(labels):4.1f}%")
    yr = collections.Counter(l["date"][:4] for l in labels)
    print("\nby year:", dict(sorted(yr.items())))
    multi = re.compile(r"\b(dafny|isabelle|coq|lean|smt|z3|cvc|tla|nusmv|spin|fdr|uppaal|frama-?c|cbmc|why3)\b", re.I)
    het = [l for l in labels
           if len(set(t.lower() for t in multi.findall(l["title"] + " " + l["abstract"]))) >= 2]
    print(f"\npapers naming >=2 distinct formal tools: {len(het)}/{len(labels)}"
          f" = {100 * len(het) / len(labels):.0f}%")
