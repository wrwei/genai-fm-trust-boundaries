"""Read-only replication trace audit. Never invokes a plant episode or transport."""
from pathlib import Path
import gzip, hashlib, importlib.util, itertools, json, math, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent

def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); sys.modules[name]=module
    spec.loader.exec_module(module); return module

def norm(x): return json.loads(json.dumps(x))
def check(x, label):
    if not x: raise AssertionError(label)
def equal(a,b,label): check(a==b if isinstance(a,(bytes,set)) else norm(a)==norm(b),label)
def close(a,b,label):
    if isinstance(a,(tuple,list)):
        check(len(a)==len(b),label)
        for x,y in zip(a,b): close(x,y,label)
    else: check(math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),label+f': {a} != {b}')

def audit_episode(name, plan, summary, folder, physics, source):
    c=sys.modules['controller']; sim=sys.modules['simulation']; plant=sys.modules['plant']
    p=sim.parameters(); config=summary['config']; pedestrian=config['pedestrian']; blackout=config['sensor_blackout']
    sup=physics.HandwrittenSupervisor() if source is None else physics.SourceSupervisor(source.decode())
    equal(summary['source_id'],sup.identity,name+' identity')
    expected_config=dict(handwritten=source is None,preference='A',pedestrian='none',sensor_blackout=None,dt=.01,horizon=120.)
    expected_config.update(plan['config']); equal(config,expected_config,name+' config')
    poses={}; speeds={n:0. for n in 'AB'}; angular={n:0. for n in 'AB'}
    for n in 'AB':
        route=p['map']['route_'+n][1:]; a,b=route[:2]
        poses[n]=(a[0],a[1],math.atan2(b[1]-a[1],b[0]-a[0]))
    goals={n:tuple(p['map']['route_'+n][-1]) for n in 'AB'}
    modes={n:'Idle' for n in 'AB'}; observations={n:None for n in 'AB'}
    acts={n:c.Actuator(n) for n in 'AB'}; queue={}; command_queue={}
    last_sent={n:None for n in 'AB'}; serials={n:0 for n in 'AB'}
    owner=None; reservation_serial=0; requested=set(); released=set(); completed=set(); person=set()
    stats=dict(collision_pairs=[],collision_witnesses=[],unresolved_pairs=[],distance_lower_bound_m=math.inf,
      continuous_intervals_checked=0,early_releases=[],grant_order=[],completion_times={},runtime_rejections=[],
      pedestrian_brakes=0,resumes_after_pedestrian=0,assumption_violated=[],assumption_detected=[])
    counts=dict(step=0,select=0,motion=0,observations=0,dropped=0,halted_checks=0)
    boundaries=[]; stopping=[]; time=0.; prior=-1.; motion_end=0.
    with gzip.open(folder/(name+'.trace.jsonl.gz'),'rt',encoding='utf-8') as stream:
      for time, group in itertools.groupby((json.loads(line) for line in stream),lambda e:e['time']):
        events=list(group); check(time>prior,name+' ordered times'); prior=time
        check(0 <= time <= config['horizon'],name+' horizon bounds')
        close(time,motion_end,name+' clock continuity')
        tick=round(time/.01); close(tick*.01,time,name+' tick')
        for e in events:
            if 'source_id' in e: equal(e['source_id'],sup.identity,name+' event identity')
        samples=[e for e in events if e['kind']=='observation']
        equal(len(samples),2 if tick%5==0 else 0,name+' sample schedule')
        for e in samples:
            q=e['packet']; n=q['robot_id']; close(q['pose'],poses[n],name+' observed pose'); close(q['speed'],speeds[n],name+' observed speed')
            equal(q,dict(robot_id=n,sample_time=time,pose=list(poses[n]),speed=q['speed'],blocked=sim.pedestrian_present(time,pedestrian),mission_revision=1,map_revision=1),name+' packet')
            close(e['receive_time'],time+.05,name+' delivery lag')
            queue.setdefault(round(time+.05,10),[]).append(c.Observation(**q)); counts['observations']+=1
        drops=[]
        for obs in queue.pop(time,[]):
            if blackout and obs.robot_id=='A' and blackout[0]<=time<blackout[1]: drops.append(dict(kind='observation_dropped',time=time,robot='A',sample_time=obs.sample_time))
            else: observations[obs.robot_id]=obs
        equal([e for e in events if e['kind']=='observation_dropped'],drops,name+' blackout delivery'); counts['dropped']+=len(drops)
        expected_aux=[]; expected_commands=[]
        steps=[e for e in events if e['kind']=='supervisor_step']
        equal([e['robot'] for e in steps],[n for n in 'AB' if n not in completed] if tick%5==0 else [],name+' monitor schedule')
        for e in steps:
            n=e['robot']; obs=observations[n]; fresh=c.usable(obs,n,time,p)
            halted=acts[n].intent=='Brake' and time-acts[n].brake_since>=(1+.05+.5*.25)/.8
            facts=dict(ObservationUsable=fresh,PedestrianBlocked=bool(obs.blocked) if fresh else False,
              OwnReservation=owner==n,Released=n in released,BodyClearOfZ=c.body_clear(obs,n,time,p),Halted=halted,
              AtGoal=fresh and math.dist(obs.pose[:2],goals[n])<=.01,TaskActive=True)
            equal(e['facts'],facts,name+' reconstructed facts'); equal(e['prior_mode'],modes[n],name+' prior mode')
            equal(e['sample_time'],obs.sample_time if obs else None,name+' latest sample')
            raw_action,raw_next=sup.step(modes[n],facts)
            equal([e['raw_action'],e['raw_next']],[raw_action,raw_next],name+' evaluated step')
            violations=physics.step_violations((raw_action,raw_next),modes[n],facts)
            action,next_mode=(('Brake','Stopped' if halted else 'BrakeRequested') if violations else (raw_action,raw_next))
            if violations: stats['runtime_rejections'].append(dict(time=time,robot=n,raw_action=raw_action,raw_next=raw_next,reasons=violations))
            equal([e['applied_action'],e['next_mode']],[action,next_mode],name+' fallback')
            movement='Brake'
            if action=='Request': requested.add(n)
            elif action=='Release':
                check(owner==n and fresh and facts['BodyClearOfZ'],name+' release authorization')
                owner=None; released.add(n)
                occupied=physics.polygon_distance(physics.rectangle(poses[n],.8,.6),physics.rectangle((12,0,0),12,5.2))<=1e-9
                if occupied: stats['early_releases'].append(dict(time=time,robot=n,pose=poses[n]))
                expected_aux.append(dict(kind='release',time=time,robot=n,actual_body_still_in_Z=occupied,source_id=sup.identity))
                movement=last_sent[n] or 'Brake'
            elif action=='Finish':
                check(fresh and facts['Released'] and facts['AtGoal'] and halted,name+' finish preconditions')
                check(math.dist(poses[n][:2],goals[n])<=.01 and abs(speeds[n])<=1e-9 and abs(angular[n])<=1e-9,name+' physical completion')
                completed.add(n); stats['completion_times'][n]=time
                expected_aux.append(dict(kind='complete',time=time,robot=n,source_id=sup.identity,goal=goals[n]))
            elif action=='Proceed': movement='Proceed'
            elif action=='Resume':
                if n in person:
                    stats['resumes_after_pedestrian']+=1; person.remove(n)
                    expected_aux.append(dict(kind='resume',time=time,robot=n,source_id=sup.identity))
            else: equal(action,'Brake',name+' action vocabulary')
            equal(e['physical_intent'],movement,name+' physical intent')
            equal(e['reservation_id'],reservation_serial if owner==n else None,name+' reservation id')
            if halted:
                check(abs(speeds[n])<=1e-8 and abs(angular[n])<=1e-8,name+' halted physical truth'); counts['halted_checks']+=1
            if modes[n]!=next_mode and (time>=10 or next_mode=='Done'):
                boundaries.append(dict(time=time,robot=n,action=action,prior=modes[n],mode=next_mode,intent=movement))
            modes[n]=next_mode; counts['step']+=1
            if action=='Brake' and facts['PedestrianBlocked'] and last_sent[n]!='Brake':
                stats['pedestrian_brakes']+=1; person.add(n)
                ev=physics.pedestrian_stopping_evidence(obs,n,time,p)
                expected_aux.append(dict(kind='pedestrian_brake',time=time,robot=n,**ev)); stopping.append(dict(time=time,robot=n,**ev))
                if ev['straight_approach_applicable'] and ev['straight_approach_condition'] is False:
                    stats['assumption_violated'].append(dict(time=time,robot=n,condition='viable_straight_approach_at_first_blocked_observation'))
            if movement!=last_sent[n]:
                serials[n]+=1
                cmd=dict(robot_id=n,seq=serials[n],intent=movement,mission_revision=1,map_revision=1,issued=time,delivery=round(time+.1,10),expiry=round(time+.3,10))
                expected_commands.append(dict(kind='command_issued',time=time,command=cmd,source_id=sup.identity,raw_action=raw_action,reservation_id=reservation_serial if owner==n else None))
                command_queue.setdefault(cmd['delivery'],[]).append(cmd); last_sent[n]=movement
        selections=[e for e in events if e['kind']=='supervisor_select']
        equal(len(selections),1 if tick%5==0 else 0,name+' selection schedule')
        for e in selections:
            f=dict(OwnerFree=owner is None,RequestA='A' in requested and 'A' not in released and c.usable(observations['A'],'A',time,p),RequestB='B' in requested and 'B' not in released and c.usable(observations['B'],'B',time,p),PreferA=config['preference']=='A',PreferB=config['preference']=='B')
            equal(e['facts'],f,name+' selection facts'); selected=sup.select(f); errors=physics.selection_violations(selected,f)
            equal(e['raw_action'],selected,name+' selection evaluation'); equal(e['applied_action'],'Defer' if errors else selected,name+' selection fallback')
            if errors: stats['runtime_rejections'].append(dict(time=time,function='select',raw_action=selected,reasons=errors))
            if not errors and selected in ('SelectA','SelectB'):
                n=selected[-1]; check(owner is None,name+' exclusive reservation'); owner=n; reservation_serial+=1; requested.discard(n); stats['grant_order'].append(n)
                expected_aux.append(dict(kind='grant',time=time,robot=n,mission_id='mission-'+n,reservation_id=reservation_serial,source_id=sup.identity))
            counts['select']+=1
        aux_kinds={'release','complete','resume','pedestrian_brake','grant'}
        equal([e for e in events if e['kind'] in aux_kinds],expected_aux,name+' boundary events')
        equal([e for e in events if e['kind']=='command_issued'],expected_commands,name+' issued commands')
        deliveries=[]
        for cmd in command_queue.pop(time,[]):
            status=acts[cmd['robot_id']].accept(c.Command(**cmd),time)
            deliveries.append(dict(kind='command_delivered',time=time,command=cmd,status=status,source_id=sup.identity))
        equal([e for e in events if e['kind']=='command_delivered'],deliveries,name+' command acceptance')
        motions=[e for e in events if e['kind']=='motion']
        equal(len(motions),0 if len(completed)==2 or time==120 else 1,name+' motion schedule')
        for e in motions:
            equal(e['duration'],.01,name+' dt'); pieces={n:[plant.MotionPiece.from_dict(q) for q in e['robots'][n]] for n in 'AB'}
            for n,seq in pieces.items():
                close(sum(q.duration for q in seq),.01,name+' piece coverage')
                for q in seq:
                    check(q.duration>=0,name+' duration'); close(q.start_pose,poses[n],name+' motion pose continuity'); close(q.initial_speed,speeds[n],name+' speed continuity')
                    end=q.initial_speed+q.acceleration*q.duration
                    check(-1e-8<=end<=1+1e-8,name+' speed bounds')
                    close(q.point_speed_bound,max(q.initial_speed,end)+abs(q.angular_velocity)*.5,name+' Lipschitz bound')
                    check(abs(q.acceleration)<=.8+1e-9 and abs(q.angular_velocity)<=math.pi/2+1e-9,name+' motion derivative bounds')
                    if acts[n].intent=='Brake': check(q.angular_velocity==0 and q.acceleration<=0,name+' effective Brake')
                    poses[n]=q.sample(q.duration); speeds[n]=0. if abs(end)<1e-9 else end; angular[n]=q.angular_velocity
            sim.assess_interval(time,.01,pieces,pedestrian,stats); counts['motion']+=1; motion_end=round(time+.01,10)
        allowed=aux_kinds|{'observation','observation_dropped','supervisor_step','supervisor_select','command_issued','command_delivered','motion'}
        check(all(e['kind'] in allowed for e in events),name+' unknown event')
    check(len(completed)==2 or time==config['horizon'],name+' incomplete trace must reach horizon')
    score=sim.score_completion(completed,{n:(poses[n],speeds[n]) for n in 'AB'},goals)
    done=score['completed_robots']
    stats.update(completed_robots=done,controller_completed_robots=sorted(completed),physical_completion_score=score,
      completion_mismatches=score['completion_mismatches'],independent_goals=goals,time=time,
      termination='complete' if len(done)==2 else 'completion_mismatch' if len(completed)==2 else 'horizon',
      reservation_owner=owner,final_poses=poses,safe_and_complete=len(done)==2 and not any(stats[k] for k in ('collision_pairs','unresolved_pairs','early_releases','runtime_rejections')),
      source_id=sup.identity,config=config)
    for k,v in stats.items():
        if k in ('final_poses','distance_lower_bound_m'):
            if k=='final_poses':
                for n in 'AB': close(v[n],summary[k][n],name+' '+k)
            else: close(v,summary[k],name+' '+k)
        else: equal(v,summary[k],name+' summary '+k)
    equal(set(stats),set(summary),name+' all summary fields audited')
    return dict(name=name,counts=counts,geometry_intervals=stats['continuous_intervals_checked'],minimum_distance_lower_bound_m=stats['distance_lower_bound_m'],final_speeds=speeds,final_modes=modes,grant_order=stats['grant_order'],completion_times=stats['completion_times'],time=time,reservation_owner=owner,safe_and_complete=stats['safe_and_complete'],boundaries=boundaries,stopping_evidence=stopping)

def main():
    s=load('replication_physics_audit_adapter',HERE/'simulate.py'); r=s.r; folder=HERE/'closed-loop'; run=HERE/'run'
    check((folder/'evidence-sha256.json').is_file(),'completed physical archive required')
    before=r.inventory(folder); manifest=before.pop('evidence-sha256.json'); equal(before,r.read_json(folder/'evidence-sha256.json'),'physical manifest')
    catalog=s.verify_live(run); physics,adaptation=s.previous.load_physics(12)
    pre=r.read_json(folder/'pre-run.json'); summary=r.read_json(folder/'summary.json')
    equal({k:r.sha(Path(k)) for k in pre['input_sha256']},pre['input_sha256'],'frozen physical input hashes')
    equal((folder/'simulate-snapshot.py').read_bytes(),(HERE/'simulate.py').read_bytes(),'adapter snapshot')
    equal((folder/'closed-loop-adapted.py').read_bytes().decode(),physics.adapted_source_bytes.decode(),'adapted source')
    equal(pre['adaptation'],adaptation,'adaptation'); equal(summary['adaptation'],adaptation,'summary adaptation')
    plan=s.episode_plan(catalog); equal(pre['plan'],plan,'episode plan'); equal(pre['dt'],.01,'dt'); equal(pre['horizon'],120.,'horizon'); equal(pre['new_model_calls'],0,'no physical calls')
    public=[{k:v for k,v in x.items() if k not in ('raw','assessment')} for x in catalog]
    mapping={sid:x['source_key'] for x in catalog for sid in x['selection']['sample_ids']}
    selection=dict(sources=public,sample_to_source_key=mapping,assessments={x['source_key']:r.compact(x['assessment']) for x in catalog},scope=s.SCOPE)
    equal(r.read_json(folder/'selection.json'),selection,'selection and acceptance')
    raws={x['source_key']:x['raw'] for x in catalog}
    for key,raw in raws.items(): check((folder/'sources'/(key+'.json')).read_bytes()==raw,'saved exact raw source')
    equal(set(summary['episodes']),{x['name'] for x in plan},'complete episode set')
    rows=[]
    for row in plan:
        name=row['name']; episode=r.read_json(folder/(name+'.json')); equal(episode,summary['episodes'][name],'episode summary identity')
        rows.append(audit_episode(name,row,episode,folder,physics,raws.get(row['source_key'])))
        print(json.dumps({'audited':name,'intervals':rows[-1]['geometry_intervals']}),flush=True)
    comparisons={}; fields=('completed_robots','collision_pairs','unresolved_pairs','early_releases','completion_mismatches','runtime_rejections','safe_and_complete')
    for key in raws:
        comparisons[key]={}
        for case,_ in s.previous.CASES:
            a=summary['episodes'][key+'_'+case]; b=summary['episodes']['reference_'+case]
            comparisons[key][case]=dict(equal_scored_outcomes=all(a[k]==b[k] for k in fields),equal_grant_order=a['grant_order']==b['grant_order'],time_difference_source_minus_handwritten=a['time']-b['time'])
    expected=dict(source_catalog=public,sample_to_source_key=mapping,unique_source_count=len(catalog),episode_count=len(plan),reference_episode_count=5,episodes=summary['episodes'],comparisons=comparisons,inputs_unchanged=True,new_model_calls=0,adaptation=adaptation,scope=s.SCOPE)
    equal(summary,expected,'complete aggregate summary')
    s.verify_live(run); equal({k:r.sha(Path(k)) for k in pre['input_sha256']},pre['input_sha256'],'post-audit inputs')
    after=r.inventory(folder); check(after.pop('evidence-sha256.json')==manifest,'post-audit manifest identity'); equal(after,before,'post-audit immutable physical archive')
    totals={k:sum(x['counts'][k] for x in rows) for k in rows[0]['counts']}
    report=dict(disposition='verified',trace_only=True,new_model_calls=0,physical_episodes_executed=0,physical_manifest_files=len(before),frozen_input_files=len(pre['input_sha256']),unique_source_count=len(catalog),episode_count=len(rows),totals=totals,geometry_intervals=sum(x['geometry_intervals'] for x in rows),minimum_distance_lower_bound_m=min(x['minimum_distance_lower_bound_m'] for x in rows),summary_sha256=r.sha(folder/'summary.json'),manifest_sha256=manifest,episodes=rows,comparisons=comparisons,
      limits='Related deterministic analytic episodes; not independent industrial tasks or a safety theorem. Straight-approach stopping evidence is inapplicable when its recorded domain conditions fail; geometric replay is a separate safety check. Preference is advisory, not a mandatory ordering obligation.')
    r.write_json(HERE/'physics-audit.json',report)
    lines=['# Independent replication physical trace audit','',f"**Verified {len(rows)} archived episodes from {len(catalog)} distinct accepted sources plus five reference cases.** No plant episode was rerun and no model or network call was made.",'',f"Checked all {len(before)} physical manifest files and {len(pre['input_sha256'])} frozen input files before and after replay. Exact accepted provider source identities, deduplication mapping, saved adapter and adapted checker imports, live deployment gate, complete episode plan, all episode summary fields and aggregate comparisons reproduce.",'',f"Re-evaluated {totals['step']:,} step and {totals['select']:,} selection decisions, reconstructing observations, blackout drops, runtime obligation checks and fallback actions, modes, physical intents, command delivery, exclusive reservation ownership, grant/release/completion events, and {totals['halted_checks']:,} physical standstill checks.",'',f"Reconstructed continuous pieces without advancing the plant and re-scored {report['geometry_intervals']:,} pair intervals using the frozen geometric oracle. Verified continuity, derivative and speed bounds, footprint clearance at release, actual goal position and standstill at completion. Minimum distance lower bound: {report['minimum_distance_lower_bound_m']:.17g} m.",'','| Episode | Grants | Completion times (s) | End (s) | Final owner | Complete and safe |','| --- | --- | --- | ---: | --- | --- |']
    for x in rows: lines.append(f"| {x['name']} | {', '.join(x['grant_order'])} | {json.dumps(x['completion_times'],sort_keys=True)} | {x['time']:.2f} | {x['reservation_owner']} | {x['safe_and_complete']} |")
    lines+=['','Stop/resume transition times, final modes/speeds, observation drop counts, and stopping-premise evidence are recorded per episode in `physics-audit.json`. Every reported summary field, including collision witnesses, runtime rejections, early releases, physical completion mismatches, and assumption lists, was checked against reconstruction.','',report['limits'],'','The pedestrian stopping diagnostic is assessed separately from geometry: an inapplicable straight stopping premise is not verified by an empty violation list. Permanent blocking can establish safe waiting only within the fixed horizon. Source preference behavior is reported through verified grant orders and reference comparisons rather than assumed to match advisory preferences.','',f"Summary SHA-256: `{report['summary_sha256']}`",f"Manifest SHA-256: `{manifest}`"]
    (HERE/'physics-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('episodes','comparisons')}),flush=True)

if __name__=='__main__': main()
