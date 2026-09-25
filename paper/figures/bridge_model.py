"""Reproduces the single-lane-bridge results in Section 10 of the AIR paper.

Exhaustive enumeration WITHIN LENGTH BOUNDS over a finite bridge model.
Finite state does not imply finite traces: C4 admits cycles.

Run it from this directory with no arguments:

    python3 bridge_model.py

It writes both artefacts the paper depends on, overwriting them in place:
  * bridge_results.json          -- every verdict, count and witness
  * cka_isabelle_case_study.png  -- Figure 2, exactly as typeset

Output is deterministic: the searches iterate over unordered sets, so the
reported witnesses are selected by a stable key rather than by first-hit
order. Two runs under different PYTHONHASHSEED values give byte-identical
results. Requires only matplotlib and numpy.

Every number quoted in Section 10 comes from here:
  * 65   controlled traces of the reference planner C0 (length <= 10)
  * the reject/pass matrix of Table 2
  * 13   controlled traces surviving when a control-gating guard meets a
         degraded advisory service, with no crossing completed
  * 1    trace (the empty one) under a block-everything guard

These are properties of THIS finite model, established by enumeration. They are
not theorems of a mechanised development; Section 12 (RQ4) carries that as
future work.
"""

from itertools import combinations
import json

SIGMA_CTRL = {f"{e}{d}" for e in ("request","grant","enter","exit") for d in ("A","B")}
SIGMA_ADV  = {"log","hmi","v2x"}
INIT = ("I", "I", None, None)   # (modeA, modeB, occupant, outstanding grant)

def steps(st, variant):
    """Enabled controlled events of a candidate planner. Returns [(event, newstate)]."""
    mA, mB, occ, gr = st
    out = []
    for d, m in (("A", mA), ("B", mB)):
        other = "B" if d == "A" else "A"
        set_m = (lambda v, d=d: (v, mB, occ, gr) if d == "A" else (mA, v, occ, gr))
        if m == "I":
            out.append((f"request{d}", set_m("R")))
        if m == "R":
            # GRANT guard is where variants differ
            if variant == "C1":                      # bug: grants while bridge occupied
                ok = gr is None
            elif variant == "C4":                    # bug: preempts an outstanding grant
                ok = occ is None
            else:                                    # C0/C2/C3 correct grant guard
                ok = occ is None and gr is None
            if ok:
                nm = (m, mB, occ, d) if d == "A" else (mA, m, occ, d)
                out.append((f"grant{d}", nm))
            if variant == "C2":                      # bug: enter without a grant
                out.append((f"enter{d}", (("C", mB, d, gr) if d == "A" else (mA, "C", d, gr))))
        if m == "R" and gr == d:
            # enter consumes the grant, except in C3 where it is left standing
            ngr = d if variant == "C3" else None
            out.append((f"enter{d}", (("C", mB, d, ngr) if d == "A" else (mA, "C", d, ngr))))
        if m == "C" and occ == d:
            out.append((f"exit{d}", (("D", mB, None, gr) if d == "A" else (mA, "D", None, gr))))
    return out

def traces(variant, maxlen=10):
    """All controlled traces up to maxlen, plus the set of reachable states."""
    seen, acc, reach = set(), set(), set()
    stack = [(INIT, ())]
    while stack:
        st, tr = stack.pop()
        reach.add(st); acc.add(tr)
        if len(tr) >= maxlen: continue
        for ev, ns in steps(st, variant):
            key = (ns, tr + (ev,))
            if key not in seen:
                seen.add(key); stack.append(key)
    return acc, reach

def violates_mutex(tr):
    """True if the trace ever has both directions occupying the bridge."""
    inside = set()
    for ev in tr:
        if ev.startswith("enter"):
            inside.add(ev[-1])
            if len(inside) > 1: return True
        elif ev.startswith("exit"):
            inside.discard(ev[-1])
    return False

def violates_grant_discipline(tr):
    """True if some enter is not backed by an unconsumed grant (contract precondition)."""
    held = set()
    for ev in tr:
        if ev.startswith("grant"): held.add(ev[-1])
        elif ev.startswith("enter"):
            if ev[-1] not in held: return True
            held.discard(ev[-1])
    return False

def contract_ok(v):
    """Per-step contract check (Dafny-like): local pre/postconditions only, no
    reasoning over whole traces.

    Violations are collected and the reported one is chosen by a stable key,
    because `reach` is a set and first-hit order would otherwise vary between
    runs -- the verdict is deterministic either way, but the witness quoted in
    the paper should be too."""
    _, reach = traces(v)
    bad = []
    for st in reach:
        mA, mB, occ, gr = st
        for ev, ns in steps(st, v):
            if ev.startswith("enter") and gr != ev[-1]:      # pre: hold the grant
                bad.append((str(st), f"enter{ev[-1]} enabled in {st} without grant"))
            if ev.startswith("grant") and occ is not None:   # pre: bridge free
                bad.append((str(st), f"{ev} enabled in {st} with bridge occupied"))
    if not bad:
        return True, None
    return False, min(bad)[1]

def can_both_cross(v, maxlen=12):
    """Progress: is there a trace in which BOTH directions complete a crossing?"""
    trs, _ = traces(v, maxlen)
    return any("exitA" in t and "exitB" in t for t in trs)

def grant_preempted(v, maxlen=10):
    """Grant preservation (a safety property, not scheduler fairness): is an outstanding grant ever overwritten before use?

    Returns the shortest witness, breaking ties lexicographically, so the
    answer is stable across runs -- the search itself iterates over unordered
    sets, which would otherwise make the reported witness arbitrary."""
    trs, _ = traces(v, maxlen)
    bad = []
    for t in trs:
        held = None
        for ev in t:
            if ev.startswith("grant"):
                if held is not None and held != ev[-1]:
                    bad.append(t); break
                held = ev[-1]
            elif ev.startswith("enter"):
                held = None
    return min(bad, key=lambda t: (len(t), t)) if bad else None

def stuck_states(v):
    _, reach = traces(v)
    return sorted((s for s in reach if not steps(s, v) and s != ("D","D",None,None)),
                  key=lambda s: tuple(str(x) for x in s))

def deployed(variant, guard, advice_available, maxlen=10):
    full, proj, reach = set(), set(), set()
    seen = set()
    stack = [((INIT, 0), (), ())]
    while stack:
        (st, adv), tr, ctr = stack.pop()
        reach.add((st, adv)); full.add(tr); proj.add(ctr)
        if len(tr) >= maxlen: continue
        if advice_available and adv < 2:
            for a in ("log", "hmi"):
                k = ((st, adv+1), tr+(a,), ctr)
                if k not in seen: seen.add(k); stack.append(k)
        for ev, ns in steps(st, variant):
            if not guard(ctr, adv, ev): continue
            k = ((ns, adv), tr+(ev,), ctr+(ev,))
            if k not in seen: seen.add(k); stack.append(k)
    return full, proj, reach

def deployed2(variant, adv_guard, advice_available, maxlen=10):
    """adv_guard(kind) -> bool decides whether an advisory artefact may be ATTACHED.
    Controlled events are never gated."""
    proj, attached, reach, seen = set(), set(), set(), set()
    stack = [((INIT, 0), (), ())]
    while stack:
        (st, adv), ctr, att = stack.pop()
        reach.add((st, adv)); proj.add(ctr); attached.add(att)
        if len(ctr) + len(att) >= maxlen: continue
        if advice_available and adv < 2:
            for kind in ("wellformed_summary", "stale_summary", "manoeuvre_command"):
                natt = att + (kind,) if adv_guard(kind) else att      # test: filter only
                k = ((st, adv+1), ctr, natt)
                if k not in seen: seen.add(k); stack.append(k)
        for ev, ns in steps(st, variant):                              # never gated
            k = ((ns, adv), ctr+(ev,), att)
            if k not in seen: seen.add(k); stack.append(k)
    return proj, attached, reach

def guard_blocks_control(guard, variant="C0", maxlen=8):
    """Return witnesses where the guard disables an otherwise-enabled controlled event."""
    bad, seen = [], set()
    stack = [((INIT, 0), ())]
    while stack:
        (st, adv), ctr = stack.pop()
        for ev, ns in steps(st, variant):
            if not guard(ctr, adv, ev):
                bad.append((ctr, adv, ev))
            elif len(ctr) < maxlen:
                k = ((ns, adv), ctr+(ev,))
                if k not in seen: seen.add(k); stack.append(k)
        if adv < 2 and len(ctr) < maxlen:
            k = ((st, adv+1), ctr)
            if k not in seen: seen.add(k); stack.append(k)
    return bad


guard_true       = lambda ctr, adv, ev: True
guard_block_all  = lambda ctr, adv, ev: False
guard_needs_advice = lambda ctr, adv, ev: not (ev.startswith("enter") and adv == 0)
adv_guard        = lambda kind: kind == "wellformed_summary"

base_traces, _ = traces("C0")
cands = ["C1","C2","C3","C4"]
keys  = ["contract","refinement","progress","fairness"]

# ---------------------------------------------------------------------------
# Figure 2 of the paper. Self-contained: no dependency on any local plotting
# helper, so this runs anywhere matplotlib is installed.
# ---------------------------------------------------------------------------
def make_figure(results, outfile="cka_isabelle_case_study.png"):
    import matplotlib as mpl
    mpl.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    mpl.rcParams.update({
        "font.family": "sans-serif", "font.size": 7,
        "axes.titlesize": 8, "axes.labelsize": 8,
        "xtick.labelsize": 6, "ytick.labelsize": 6,
        "axes.linewidth": 0.8, "xtick.major.width": 0.8,
        "ytick.major.width": 0.8, "figure.dpi": 300, "savefig.dpi": 300,
    })
    CATCH, MISS, GREY = "#b2182b", "#f0f0f0", "#8c8c8c"
    C_UP, C_DN = "#4393c3", "#d6604d"

    clabel = {"C1": "grants while\nbridge occupied",
              "C2": "enters without\na grant",
              "C3": "grant not\nconsumed on entry",
              "C4": "re-grants over an\noutstanding grant"}
    discs = ["local\ncontracts", "occupancy",
             "progress\nchecks", "grant\npreservation"]
    M = np.array([[0 if results["dev"][c][k] else 1 for k in keys] for c in cands])

    fig = plt.figure(figsize=(7.2, 3.40))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.16, 1.0], wspace=0.44,
                          left=0.148, right=0.985, top=0.80, bottom=0.315)

    # (a) development-time discriminator x defect matrix
    axa = fig.add_subplot(gs[0, 0])
    for i in range(len(cands)):
        for j in range(len(discs)):
            caught = M[i, j] == 1
            axa.add_patch(mpl.patches.Rectangle((j - .5, i - .5), 1, 1,
                          facecolor=CATCH if caught else MISS,
                          edgecolor="white", linewidth=1.4))
            axa.text(j, i, "reject" if caught else "pass", ha="center",
                     va="center", fontsize=6,
                     color="white" if caught else "#666666",
                     fontweight="bold" if caught else "normal")
    axa.set_xticks(range(len(discs))); axa.set_xticklabels(discs, fontsize=6)
    axa.set_yticks(range(len(cands)))
    axa.set_yticklabels([f"{c}: {clabel[c]}" for c in cands], fontsize=6)
    axa.set_xlim(-.5, len(discs) - .5); axa.set_ylim(len(cands) - .5, -.5)
    axa.set_title("Coverage of selected obligation sets",
                  fontsize=8, loc="left", pad=8)
    for s in axa.spines.values():
        s.set_visible(False)
    axa.tick_params(length=0)
    axa.text(-0.30, 1.06, "a", transform=axa.transAxes,
             fontsize=9, fontweight="bold", va="bottom")

    # (b) runtime composition
    axb = fig.add_subplot(gs[0, 1])
    scen = [("permissive", "no guard"),
            ("control_gating", "guard gates\ncontrol events"),
            ("advisory_only", "guard gates\nadvice only")]
    x = np.arange(len(scen)); w = 0.36
    up = [results["runtime"][f"{k}/advice_up"]["n_proj"] for k, _ in scen]
    dn = [results["runtime"][f"{k}/advice_down"]["n_proj"] for k, _ in scen]
    n_plan = results["n_plan_traces"]
    axb.bar(x - w / 2, up, w, color=C_UP, label="advisory service available")
    axb.bar(x + w / 2, dn, w, color=C_DN, label="advisory service degraded")
    axb.axhline(n_plan, color=GREY, lw=1, ls=(0, (4, 2)), zorder=1)
    axb.text(-0.5, 96, f"reference planner: {n_plan} traces", fontsize=6,
             color=GREY, ha="left", va="top")
    for xi, v in zip(x - w / 2, up):
        axb.text(xi, v + 2.5, str(v), ha="center", fontsize=6, color=C_UP)
    for xi, v in zip(x + w / 2, dn):
        if v != dn[1]:
            axb.text(xi, v + 2.5, str(v), ha="center", fontsize=6, color=C_DN)
    axb.text(1 + w / 2 + 0.24, dn[1] / 2, str(dn[1]), ha="left", va="center",
             fontsize=6, color=C_DN)
    axb.annotate("no crossing\ncompletes", xy=(1 + w / 2, dn[1] + 3.5),
                 xytext=(1.30, 30), fontsize=6, color=C_DN,
                 ha="center", va="bottom", zorder=5,
                 arrowprops=dict(arrowstyle="->", color=C_DN, lw=.9,
                                 shrinkB=1, connectionstyle="arc3,rad=0.15"))
    axb.set_xticks(x); axb.set_xticklabels([l for _, l in scen], fontsize=6)
    axb.set_ylabel("controlled traces reachable", fontsize=8)
    axb.set_xlim(-0.55, 2.55); axb.set_ylim(0, 100)
    axb.set_yticks([0, 20, 40, 60, 80])
    axb.set_title("All three satisfy bounded trace inclusion",
                  fontsize=8, loc="left", pad=8)
    axb.legend(frameon=False, fontsize=6, loc="upper center",
               bbox_to_anchor=(0.46, -0.235), ncol=1, handlelength=1.1,
               borderpad=0, labelspacing=0.35, handletextpad=0.5)
    axb.spines["top"].set_visible(False); axb.spines["right"].set_visible(False)
    axb.text(-0.30, 1.06, "b", transform=axb.transAxes,
             fontsize=9, fontweight="bold", va="bottom")

    fig.savefig(outfile, dpi=300, bbox_inches="tight")
    return outfile


if __name__ == "__main__":
    dev = {}
    for v in ("C0","C1","C2","C3","C4"):
        trs, _ = traces(v)
        cok, cwhy = contract_ok(v)
        dev[v] = dict(traces=len(trs), contract=cok,
                      refinement=not any(violates_mutex(t) for t in trs),
                      progress=(not stuck_states(v)) and can_both_cross(v),
                      fairness=grant_preempted(v) is None,
                      contract_witness=cwhy,
                      stuck=[list(map(str,s)) for s in stuck_states(v)[:2]],
                      preempt_witness=list(grant_preempted(v)) if grant_preempted(v) else None)
    runtime = {}
    for gn, g in (("permissive",guard_true),("control_gating",guard_needs_advice),
                  ("block_all",guard_block_all)):
        for av in (True, False):
            _, p, _ = deployed("C0", g, advice_available=av)
            runtime[f"{gn}/advice_{'up' if av else 'down'}"] = dict(
                n_proj=len(p), cka_holds=p <= base_traces,
                safety=not any(violates_mutex(t) for t in p),
                progress_both=any("exitA" in t and "exitB" in t for t in p),
                progress_any=any("exitA" in t or "exitB" in t for t in p),
                control_live=not guard_blocks_control(g))
    for av in (True, False):
        p, att, _ = deployed2("C0", adv_guard, advice_available=av)
        runtime[f"advisory_only/advice_{'up' if av else 'down'}"] = dict(
            n_proj=len(p), cka_holds=p <= base_traces,
            safety=not any(violates_mutex(t) for t in p),
            progress_both=any("exitA" in t and "exitB" in t for t in p),
            progress_any=any("exitA" in t or "exitB" in t for t in p),
            control_live=True, attached=sorted({k for a in att for k in a}))
    json.dump(dict(n_plan_traces=len(base_traces),
                   sigma_ctrl=sorted(SIGMA_CTRL), sigma_adv=sorted(SIGMA_ADV),
                   dev=dev, runtime=runtime),
              open("bridge_results.json","w"), indent=1)
    print("n_plan_traces =", len(base_traces))
    for v, d in dev.items():
        print(v, {k: d[k] for k in keys})
    for k, d in runtime.items():
        print(f"{k:34}", {kk: d[kk] for kk in ("n_proj","cka_holds","control_live","progress_both")})

    results = dict(n_plan_traces=len(base_traces), dev=dev, runtime=runtime)
    print("wrote", make_figure(results))
