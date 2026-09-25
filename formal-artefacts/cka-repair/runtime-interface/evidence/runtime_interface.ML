structure Runtime_Interface : sig
  datatype command = Submit | Service | SetPermission of bool | Advice of bool |
    LostAck | Poll
  datatype event = Policy of bool | Commit | Hidden of command
  datatype phase = Idle | Pending | Approved | Completed
  type 'a istate_ext
  val permitted : 'a istate_ext -> bool
  val stage : 'a istate_ext -> phase
  val step : unit istate_ext -> command -> unit istate_ext * event
  val initial : unit istate_ext
  val run_state :
    (unit istate_ext -> command -> unit istate_ext * event) ->
      unit istate_ext -> command list -> unit istate_ext
  val run_trace :
    (unit istate_ext -> command -> unit istate_ext * event) ->
      unit istate_ext -> command list -> event list
  val make_state : bool -> phase -> bool -> unit istate_ext
  val retry_step : unit istate_ext -> command -> unit istate_ext * event
  val cached_step : unit istate_ext -> command -> unit istate_ext * event
  val advice_available : 'a istate_ext -> bool
  val advice_blocked_step :
    unit istate_ext -> command -> unit istate_ext * event
end = struct

datatype command = Submit | Service | SetPermission of bool | Advice of bool |
  LostAck | Poll;

datatype event = Policy of bool | Commit | Hidden of command;

datatype phase = Idle | Pending | Approved | Completed;

datatype 'a istate_ext = Istate_ext of bool * phase * bool * 'a;

fun fst (x1, x2) = x1;

fun snd (x1, x2) = x2;

fun advice_available_update advice_availablea
  (Istate_ext (permitted, stage, advice_available, more)) =
  Istate_ext (permitted, stage, advice_availablea advice_available, more);

fun equal_phase Approved Completed = false
  | equal_phase Completed Approved = false
  | equal_phase Pending Completed = false
  | equal_phase Completed Pending = false
  | equal_phase Pending Approved = false
  | equal_phase Approved Pending = false
  | equal_phase Idle Completed = false
  | equal_phase Completed Idle = false
  | equal_phase Idle Approved = false
  | equal_phase Approved Idle = false
  | equal_phase Idle Pending = false
  | equal_phase Pending Idle = false
  | equal_phase Completed Completed = true
  | equal_phase Approved Approved = true
  | equal_phase Pending Pending = true
  | equal_phase Idle Idle = true;

fun permitted_update permitteda
  (Istate_ext (permitted, stage, advice_available, more)) =
  Istate_ext (permitteda permitted, stage, advice_available, more);

fun stage_update stagea (Istate_ext (permitted, stage, advice_available, more))
  = Istate_ext (permitted, stagea stage, advice_available, more);

fun permitted (Istate_ext (permitted, stage, advice_available, more)) =
  permitted;

fun stage (Istate_ext (permitted, stage, advice_available, more)) = stage;

fun step s Submit =
  (stage_update
     (fn _ => (if equal_phase (stage s) Idle then Pending else stage s)) s,
    Hidden Submit)
  | step s Service =
    (if equal_phase (stage s) Pending andalso permitted s
      then (stage_update (fn _ => Approved) s, Hidden Service)
      else (if equal_phase (stage s) Approved andalso permitted s
             then (stage_update (fn _ => Completed) s, Commit)
             else (s, Hidden Service)))
  | step s (SetPermission b) = (permitted_update (fn _ => b) s, Policy b)
  | step s (Advice b) =
    (advice_available_update (fn _ => b) s, Hidden (Advice b))
  | step s LostAck = (s, Hidden LostAck)
  | step s Poll = (s, Hidden Poll);

val initial : unit istate_ext = Istate_ext (true, Idle, false, ());

fun run_state k s [] = s
  | run_state k s (c :: cs) = run_state k (fst (k s c)) cs;

fun run_trace k s [] = []
  | run_trace k s (c :: cs) = snd (k s c) :: run_trace k (fst (k s c)) cs;

fun make_state permission phase available =
  Istate_ext (permission, phase, available, ());

fun retry_step s LostAck =
  (stage_update
     (fn _ => (if equal_phase (stage s) Completed then Approved else stage s))
     s,
    Hidden LostAck)
  | retry_step s Submit = step s Submit
  | retry_step s Service = step s Service
  | retry_step s (SetPermission v) = step s (SetPermission v)
  | retry_step s (Advice v) = step s (Advice v)
  | retry_step s Poll = step s Poll;

fun cached_step s Service =
  (if equal_phase (stage s) Approved
    then (stage_update (fn _ => Completed) s, Commit) else step s Service)
  | cached_step s Submit = step s Submit
  | cached_step s (SetPermission v) = step s (SetPermission v)
  | cached_step s (Advice v) = step s (Advice v)
  | cached_step s LostAck = step s LostAck
  | cached_step s Poll = step s Poll;

fun advice_available (Istate_ext (permitted, stage, advice_available, more)) =
  advice_available;

fun advice_blocked_step s Service =
  (if equal_phase (stage s) Approved andalso not (advice_available s)
    then (s, Hidden Service) else step s Service)
  | advice_blocked_step s Submit = step s Submit
  | advice_blocked_step s (SetPermission v) = step s (SetPermission v)
  | advice_blocked_step s (Advice v) = step s (Advice v)
  | advice_blocked_step s LostAck = step s LostAck
  | advice_blocked_step s Poll = step s Poll;

end; (*struct Runtime_Interface*)
