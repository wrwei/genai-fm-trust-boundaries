# Frozen finite HOL/Python interface

Robots: `A`, `B`; optional robots: null, A, B. Core state fields in order: `req_a`, `req_b` (bool), `owner` (optional robot), `blocked`, `fresh` (bool), `pending`, `command` (optional robot). Initial core: false,false,null,false,true,null,null.

Inputs (trusted unless noted): `Register(A|B)`; `Observe(blocked,fresh)`; `Validate(intent)` (optional robot); `Commit`; `Issue(A|B)`; `Apply`; `Release(A|B,whole_clear)`; `Service(intent)`; `RequestAdvice`; provider `Reply(optional robot)`; `Consume(optional robot)`.

Core semantics: legal grant r iff request r, owner=null, not blocked, fresh. Register sets request. Observe sets permission; preserves pending and command (saved intents are not permissions; Commit/Apply recheck current permission). Validate stores intent only when pending=null and intent is legal. Commit grants pending only if currently legal; on success sets owner, clears pending and request, emits Grant(r); otherwise clears pending. Service(intent) is Validate(intent) when pending=null, otherwise Commit. Issue(r) stores command=r iff owner=r and usable permission. Apply emits Proceed(r) iff command=r, owner=r and usable permission, then clears command regardless. Release(r,true) clears owner and command iff owner=r, emits Released(r); false whole_clear does nothing. Other inputs leave core unchanged.

Visible events: Registered(r), Observed(blocked,fresh), Grant(r), Issued(r), Proceed(r), Released(r). Register/Observe always emit their environment event. All other unsuccessful/internal inputs emit no visible event. Permission updates MUST remain visible.

Advice state (fixed-mission typed abstraction; core-only exhaustive conformance): `requested` bool and `mailbox` optional robot, initially false/null. RequestAdvice sets requested=true (idempotent); Reply(r) fills an empty mailbox iff requested and r is nonnull; duplicates/invalid null replies do nothing. Consume(r) is permitted iff r=mailbox, then preserves mailbox (read-only consumption). All other inputs preserve advice state. Operational runs include only permitted Consume; all core inputs are total. Trusted `Consume` and `Validate`/`Service` are separate events, not provider events. This finite core does NOT claim mission-ID/epoch implementation refinement: one fixed mission, no request cancellation/reuse, synchronous current trusted state at Apply; advice identity parsing is abstracted to Reply. Each robot's request can be registered again at the abstract level; the intended one-task scenario registers A/B once.

Source selector is supplied outside guard as `intent`; safety allows arbitrary intent. For liveness and concrete A/B/no-advice witnesses use selector F: legal advised robot if present, else legal A, else legal B, else null. FIFO scope is simultaneous registration with fixed A-before-B; no general arrival order is modeled. Root must check original source against F; HOL does not certify source bytes.

Exports planned: exhaustive core state/input transition rows, with independently HOL-evaluated outputs. Advice transition conformance can be separate. Further changes to this vocabulary will be messaged explicitly.


Export order and encoding: see README. Actual paths are `hol/export/AMR_Advisory_V2.AMR_Protocol/core-transitions.csv` and `selector.csv`. The latter has state7 + advice + F-result, optional robot encoded null/A/B as0/1/2. Core rows are state7 + next-state7 + event3, 27inputs per state. Enumeration is the executable HOL `all_states`/`all_inputs`, with no Python-generated expected values.


Source-restricted operational profile: `source_next`/`S_source` refine the broad safety machine. At a trusted Service or Validate when pending=null, intent must equal HOL F(core,mailbox). That operation atomically reads the persistent slot and latches the choice; Consume is optional read-only bookkeeping, not the selection latch. When pending is nonnull, newer advice cannot change it. Broad S_HOL still allows arbitrary candidate intent for provider-independent safety. Parsing and unbounded mission identity remain abstracted.
