(* Run from this directory after exporting evidence/runtime_interface.ML.
   This adapter only enumerates inputs and serializes generated-code results. *)
use "evidence/runtime_interface.ML";

structure R = Runtime_Interface;

val phases = [R.Idle, R.Pending, R.Approved, R.Completed];
val commands = [R.Submit, R.Service, R.SetPermission false, R.SetPermission true,
                R.Advice false, R.Advice true, R.LostAck, R.Poll];
val states = List.concat (map (fn p => List.concat (map (fn permission =>
  map (fn available => R.make_state permission p available) [false, true])
  [false, true])) phases);

fun phaseCode R.Idle = 0
  | phaseCode R.Pending = 1
  | phaseCode R.Approved = 2
  | phaseCode R.Completed = 3;

fun commandCode R.Submit = 0
  | commandCode R.Service = 1
  | commandCode (R.SetPermission false) = 2
  | commandCode (R.SetPermission true) = 3
  | commandCode (R.Advice false) = 4
  | commandCode (R.Advice true) = 5
  | commandCode R.LostAck = 6
  | commandCode R.Poll = 7;

fun stateCode s = 4 * phaseCode (R.stage s) +
  (if R.permitted s then 2 else 0) + (if R.advice_available s then 1 else 0);

fun eventCode R.Commit = 1
  | eventCode (R.Policy false) = 2
  | eventCode (R.Policy true) = 3
  | eventCode (R.Hidden c) = 10 + commandCode c;

val kernels = [("guarded", R.step), ("cached", R.cached_step),
               ("advice_blocked", R.advice_blocked_step), ("retry", R.retry_step)];

val _ = if stateCode R.initial = 2 then () else raise Fail "Unexpected initial state";
val _ = print "profile,state,command,target,event\n";
val _ = List.app (fn (name, kernel) => List.app (fn s => List.app (fn c =>
  let val (target, event) = kernel s c in
    print (String.concatWith "," [name, Int.toString (stateCode s),
      Int.toString (commandCode c), Int.toString (stateCode target),
      Int.toString (eventCode event)] ^ "\n")
  end) commands) states) kernels;
