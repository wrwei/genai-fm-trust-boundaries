"""Independent retained-trace audit; does not import physical or its geometric oracle."""
import gzip, hashlib, json, math, sys
from collections import Counter
from pathlib import Path
from source_check import language, ROOT
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'amr-corridor'))
from plant import RobotPlant

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b):
    if isinstance(a,dict): return a.keys()==b.keys() and all(close(v,b[k]) for k,v in a.items())
    if isinstance(a,(tuple,list)): return len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
    if isinstance(a,(float,int)) and not isinstance(a,bool): return abs(a-b)<1e-8
    return a==b

def gap(a,ad,b,bd):
    """Largest separating projection gap of two oriented rectangles (unit axes)."""
    ca,sa=math.cos(a[2]),math.sin(a[2]); cb,sb=math.cos(b[2]),math.sin(b[2])
    au=((ca,sa),(-sa,ca)); bu=((cb,sb),(-sb,cb))
    dot=lambda x,y:x[0]*y[0]+x[1]*y[1]
    d=(b[0]-a[0],b[1]-a[1])
    return max(abs(dot(d,u))-sum(ad[i]/2*abs(dot(au[i],u)) for i in (0,1))-sum(bd[i]/2*abs(dot(bu[i],u)) for i in (0,1)) for u in au+bu)

def pose(p,t):
    x,y,h=p['start_pose']; d=p['initial_speed']*t+p['acceleration']*t*t/2
    return x+math.cos(h)*d,y+math.sin(h)*d,h+p['angular_velocity']*t
def at(ps,t):
    for p in ps:
        if t<=p['duration']+1e-10:return pose(p,min(t,p['duration']))
        t-=p['duration']
    raise AssertionError('uncovered motion')
def speed_bound(ps):
    return max(max(abs(p['initial_speed']),abs(p['initial_speed']+p['acceleration']*p['duration']))+.5*abs(p['angular_velocity']) for p in ps)

def sweep(a,ad,av,b,bd,bv,dt,counts,lo=0.,hi=None):
    hi=dt if hi is None else hi; mid=(lo+hi)/2
    g=gap(a(mid),ad,b(mid),bd); counts['geometry_nodes']+=1
    # A fixed axis chosen at midpoint remains separating if neither body can close
    # the projection gap under its independent corner-speed bound.
    if g>(av+bv)*(hi-lo)/2+1e-10:return
    assert g>0, 'overlapping midpoint'
    assert hi-lo>1e-7, 'unresolved continuous interval'
    sweep(a,ad,av,b,bd,bv,dt,counts,lo,mid);sweep(a,ad,av,b,bd,bv,dt,counts,mid,hi)

def main():
    batch=HERE/'evidence/physical/20260921T144921Z'
    plan=json.loads((batch/'plan.json').read_bytes()); summary=json.loads((batch/'summary.json').read_bytes())
    p=json.loads((batch/'effective-parameters.json').read_bytes())
    assert sha(HERE/'physical-contract.md')==plan['contract_sha256']
    for path,h in plan['identities']['files'].items():assert sha(HERE.parent/path)==h
    assert hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest()==plan['identities']['effective_parameters_sha256']
    assert p['timing']['brake_delivery_and_onset_upper_bound']==.10 and p['timing']['total_reaction_upper_bound']==.27
    selected=json.loads((HERE/'evidence/source/summary.json').read_bytes())['selected']; raw=(ROOT/selected['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==plan['identities']['source_sha256']
    program=language.parse_program(raw.decode())
    allrows={}; results=[]
    for s in summary['results']:
        name=s['run_id']; trace=batch/s['trace']; assert sha(trace)==s['trace_sha256']
        assert json.loads((batch/(name+'.summary.json')).read_bytes())==s
        with gzip.open(trace,'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
        allrows[name]=rows; counts=Counter(); releases=[]; finishes=[]; violations=[]; grants=[]
        braking=name.startswith('Brake'); gaprun=name.startswith('E3')
        robots={'A':RobotPlant([(s['observed_pose'][0],0),(16,0)],initial_speed=1)} if braking else {r:RobotPlant(p['map']['route_'+r][1:]) for r in 'AB'}
        intent={r:('Proceed' if braking else 'Brake') for r in robots}; previous_state=None; received={}; sampled={}
        for row in sorted(rows,key=lambda r:r['time']):
            k=row['kind']; t=row['time']; counts[k]+=1
            if k=='source_step':
                assert list(language.eval_step(program,row['prior_mode'],row['facts']))==[row['raw_action'],row['raw_next']]
                assert row['source_id']==selected['source_sha256']
            if k=='source_select':assert language.eval_select(program,row['facts'])==row['raw_action']
            if k=='protocol':
                before=row['before']; accepted=True
                if previous_state is not None:assert before==previous_state
                previous_state=row['after']
                for event in row['events']:
                    op,*args=event
                    if op=='Grant':
                        grants.append(args[0]);accepted &= before['owner'] is None and before['req_'+args[0].lower()] and before['fresh'] and not before['blocked']
                    if op in ('Issued','Proceed'):accepted &= before['owner']==args[0] and before['fresh'] and not before['blocked']
                assert accepted==row['reference_accepted']
                if not accepted:violations.append({'time':t,'events':row['events']})
            if k=='command_applied':
                r='A' if braking or gaprun else row['command']['robot']
                assert close(robots[r].pose,row['actual_pose']) and close(robots[r].speed,row['actual_speed'])
                if not braking and not gaprun:
                    c=row['command']; state=row['current_state']; valid=c['delivery']-1e-9<=t<=c['expiry']+1e-9
                    if c['intent']=='Proceed' and c['scope']=='reservation_zone':
                        valid &= state['owner']==r and c['generation']==row['reservation_generation'] and c['mission']=='mission-'+r and state['fresh'] and not state['blocked']
                    elif c['intent']=='Proceed':valid &= r in [v['robot'] for v in releases] and t-received[r]['sample_time']<=.1+1e-9 and not received[r]['blocked']
                    assert bool(valid)==row['current_check_verdict']
                if braking:intent[r]='Brake'
                elif row['current_check_verdict']:intent[r]=row['command']['intent']
            if k=='observation_sample':
                o=row['packet']; r=o['robot_id'];assert close(o['pose'],robots[r].pose) and close(o['speed'],robots[r].speed)
                sampled[(r,o['sample_time'])]=o
                if not braking:
                    trigger=s.get('pedestrian_trigger'); mode=s.get('config',{}).get('pedestrian','none')
                    blocked=trigger is not None and t>=trigger['time'] and (mode=='permanent' or t<trigger['time']+7)
                    assert o['blocked']==blocked
                if 'receive_time' in row:assert close(row['receive_time']-t,.05)
                if name.startswith('E4'):assert o['blocked'] is False
            if k=='observation_received':
                o=row['packet'];r=o['robot_id']; assert o==sampled[(r,o['sample_time'])] and close(t-o['sample_time'],.05);received[r]=o
            if k=='command_issued' and 'command' in row:assert close(row['command']['delivery']-t,.10)
            if k=='release':
                assert close(row['pose'],robots[row['robot']].pose)
                overlap=gap(row['pose'],(.8,.6),(12,0,0),(12,5.2))<=0
                assert overlap==row['actual_body_still_in_Z']; releases.append({'time':t,'robot':row['robot'],'overlap':overlap})
            if k=='complete':
                r=row['robot']; assert close(row['actual_pose'],robots[r].pose) and close(row['actual_speed'],robots[r].speed)
                assert abs(robots[r].speed)<1e-9 and math.dist(robots[r].pose[:2],p['map']['route_'+r][-1])<=.01
                finishes.append({'robot':r,'time':t})
            if k=='pedestrian_trigger':
                x,y,h=row['pose'];assert close(row['pose'],robots[row['robot']].pose) and abs(y)<1e-9 and abs(h)<1e-9 and 8<=x<=16 and x+.4<11.5
            if k=='motion':
                pieces={'A':row['pieces']} if braking else row['robots']
                if not braking and not gaprun:
                    trigger=s.get('pedestrian_trigger');mode=s['config']['pedestrian']
                    present=trigger is not None and t+.005>=trigger['time'] and (mode=='permanent' or t+.005<trigger['time']+7)
                    assert row['actual_pedestrian_present']==present
                for r,ps in pieces.items():
                    actual=[v.to_dict() for v in robots[r].advance(row['duration'],intent[r])]
                    assert close(actual,ps),(name,t,r,'plant mismatch')
                    counts['plant_robot_intervals']+=1
                bodies={r:(lambda u,ps=ps:at(ps,u),(.8,.6),speed_bound(ps)) for r,ps in pieces.items()}
                pairs=[]
                if braking:pairs=[(bodies['A'],(lambda u:(12,0,0),(1,7),0))]
                else:
                    pairs.append((bodies['A'],bodies['B']))
                    for body in bodies.values():
                        for x in (9.75,14.25):
                            for y in (-.87,.87):pairs.append((body,(lambda u,x=x,y=y:(x,y,0),(3.5,.14),0)))
                        if row.get('actual_pedestrian_present'):
                            trigger=row['pedestrian_trigger']; cap=0 if row['pedestrian_mode']=='permanent' else 3.5
                            pairs.append((body,(lambda u,t=t,trigger=trigger,cap=cap:(12,min(cap,-3.5+max(0,t+u-trigger)),math.pi/2),(.5,.5),1)))
                for a,b in pairs:
                    sweep(a[0],a[1],a[2],b[0],b[1],b[2],row['duration'],counts);counts['continuous_pair_intervals']+=1
        assert len(violations)==len(s['reference_violations']) and grants==s.get('grant_order',[])
        assert sum(r['overlap'] for r in releases)==len(s['early_releases'])
        if 'final_poses' in s:
            for r in robots:assert close(robots[r].pose,s['final_poses'][r]) and close(robots[r].speed,s['final_speeds'][r])
        else:assert close(robots['A'].pose,s['final_pose']) and close(robots['A'].speed,s['final_speed'])
        if braking:
            bound=1.05*.22+.5*.5*.22**2+(1.05+.5*.22)**2/1.6+.05+.2
            assert close(bound,s['bound']) and s['condition']==(name=='Brake-inside')
            assert close(11.5-robots['A'].pose[0]-.4,s['standstill_margin']) and robots['A'].speed==0
        if name in ('P-A','P-B','P-none','E2-whole','E4-fifo','B2-temporary'):
            assert len(finishes)==2 and not violations and not any(r['overlap'] for r in releases)
            assert grants[0]==('B' if name=='P-B' else 'A')
        elif name=='E2-center':assert sum(r['overlap'] for r in releases)==2
        elif gaprun:
            assert len(violations)==int(name.endswith('bad'))
            assert (robots['A'].speed>0)==(name=='E3b-bad')
        elif name=='E4-wait':assert not grants and not finishes and s['time']==120
        elif name=='B2-permanent':assert not finishes and s['time']==120 and s['pedestrian_trigger'] is not None
        if not braking:assert not s['collision_pairs'] and not s['unresolved_pairs']
        results.append(dict(run_id=name,counts=dict(counts),releases=releases,finishes=finishes,violations=violations,grant_order=grants,trace_sha256=sha(trace)))
        print(name,dict(counts),flush=True)
    a,b=allrows['E2-center'],allrows['E2-whole']; prefix=next(i for i,(x,y) in enumerate(zip(a,b)) if x!=y)
    out=dict(batch=plan['batch'],audit_script_sha256=sha(Path(__file__)),plan_sha256=sha(batch/'plan.json'),summary_sha256=sha(batch/'summary.json'),source_sha256=selected['source_sha256'],runs=results,expected_outcomes_independently_confirmed=15,e2_common_prefix_records=prefix,e2_first_divergence_time=a[prefix]['time'],totals=dict(sum((Counter(r['counts']) for r in results),Counter())),all_assertions_passed=True,scope='All retained source outputs and plant intervals replayed; independent OBB SAT plus corner-speed continuous separation certificates. Shared historical source interpreter and plant, independent geometry; no hardware/refinement proof.')
    (HERE/'evidence/physical-audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out['totals'],indent=2))
if __name__=='__main__':main()
