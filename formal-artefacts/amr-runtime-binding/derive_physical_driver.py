"""Create an inspectable additive driver; never edit or dynamically patch v2."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
origin = HERE.parent/'amr-advisory-v2/physical.py'
text = origin.read_text(encoding='utf-8')
node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == 'run_episode')
original = '\n'.join(text.splitlines()[node.lineno-1:node.end_lineno]) + '\n'
derived = original

def change(old, new):
    global derived
    if derived.count(old) != 1:
        raise ValueError('expected exactly one origin fragment: ' + old[:80])
    derived = derived.replace(old, new)

change('def run_episode(*,advice=None,center_clear=False,wait_advice=False,pedestrian=\'none\',horizon=120.,emit=None):',
       'def run_episode(*,advice_events=(),pedestrian=\'none\',horizon=120.,emit=None):')
change('    s=Core(fresh=False); generation=0; permission_version=0; trigger=None; seq=0\n'
       "    mailbox=AdviceMailbox('physical-request','fixed-A-B-v1')\n"
       "    if advice is not None: mailbox.receive('physical-request','fixed-A-B-v1',json.dumps({'prefer':advice}))\n"
       '    latched=mailbox.latch()',
       "    runtime=Runtime('req','ctx',source=source)\n"
       '    s=runtime.core; generation=0; permission_version=0; trigger=None; seq=0\n'
       '    deliveries={}\n'
       '    for at,req,ctx,payload in advice_events:\n'
       '        if at < 0 or abs(at/.01-round(at/.01)) > 1e-7:\n'
       "            raise ValueError('advice times must be nonnegative 10ms ticks')\n"
       '        deliveries.setdefault(round(at/.01),[]).append((req,ctx,payload))')
change('        before=s; s,events=step(s,inp)',
       "        before=s; bound=runtime.local(inp); s=runtime.core; events=bound['events']\n"
       "        record('adapter',t,**bound)\n"
       "        actual_input=bound['event'][1]\n"
       "        if bound['source'] is not None:\n"
       "            record('source_select',t,**bound['source'],mailbox=bound['source']['latch'])")
change('        row=dict(before=asdict(before),input=inp,after=asdict(s),events=events,reference_accepted=accepted,',
       '        row=dict(before=asdict(before),input=actual_input,after=asdict(s),events=events,reference_accepted=accepted,')
change("    for r in 'AB':transition(('Register',r),0)\n    record('mailbox',0,**latched)",
       "    transition(('RequestAdvice',),0)\n    transition(('Observe',False,False),0)\n"
       "    for r in 'AB':transition(('Register',r),0)")
change('        t=round(tick*.01,10)',
       '        t=round(tick*.01,10)\n'
       '        for req,ctx,payload in deliveries.pop(tick,[]):\n'
       "            record('adapter',t,**runtime.receive(req,ctx,payload))")
change("                clear=(fresh and (o.pose[0]>18 if r=='A' else o.pose[0]<6)) if center_clear else body_clear(o,r,t,p)",
       '                clear=body_clear(o,r,t,p)')
change("            if s.owner is None and not (wait_advice and latched['advice'] is None):\n"
       "                selected,decision=source.select(s,latched['advice'])\n"
       "                record('source_select',t,**decision,mailbox=latched)\n"
       "                transition(('Validate',selected),t);transition(('Commit',),t)\n"
       "            elif wait_advice and s.owner is None:record('wait_advice',t,source_select_called=False,current_state=asdict(s))",
       "            if s.owner is None:\n"
       "                transition(('Validate',),t);transition(('Commit',),t)")
change('                 config=dict(advice=advice,center_clear=center_clear,wait_advice=wait_advice,pedestrian=pedestrian,horizon=horizon))',
       '                 config=dict(advice_events=advice_events,pedestrian=pedestrian,horizon=horizon))')
header = '''"""Additive physical driver derived from v2; see physical-driver.diff for exact changes.
Runtime receives replies on serial simulation ticks. No real-time network claim.
"""
from dataclasses import asdict
import math
from binding import Runtime, Core, SourceController, reference_accepts
from physical import (effective_parameters, empty_stats, overlaps, RobotPlant, Observation,
                      usable, body_clear, braking_distance, assess_interval, sweep_check,
                      score_completion)

'''
(HERE/'physical_binding.py').write_text(header + derived, encoding='utf-8')
(HERE/'physical-driver.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),
    derived.splitlines(True), fromfile='v2/run_episode', tofile='binding/run_episode')), encoding='utf-8')
(HERE/'physical-driver-origin.json').write_text(json.dumps(dict(
    origin='amr-advisory-v2/physical.py', origin_sha256=hashlib.sha256(origin.read_bytes()).hexdigest(),
    derived_sha256=hashlib.sha256((HERE/'physical_binding.py').read_bytes()).hexdigest(),
    scope='function copied with explicit adapter substitutions; same plant/geometry; v2 unchanged'), indent=2)+'\n')
print('Created additive driver and exact function diff')
