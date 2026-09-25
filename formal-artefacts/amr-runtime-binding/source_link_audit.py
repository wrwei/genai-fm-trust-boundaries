"""Reconstruct source facts/modes and tie each command to its generating action.
Independent of the physical driver, controller.usable and controller.body_clear.
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'amr-advisory-v2'))
from source_check import language


class SourceLinkAudit:
    def __init__(self, params, program):
        self.params, self.program = params, program
        self.core = None
        self.received = {}
        self.modes = dict.fromkeys('AB', 'Idle')
        self.intents = dict.fromkeys('AB', 'Brake')
        self.since = dict.fromkeys('AB', 0.)
        self.last = dict.fromkeys('AB')
        self.released = set()
        self.release_before = {}
        self.finish_before = {}
        self.expected_command = {}
        self.issued_permissions = []
        self.applied_permissions = []
        self.commands = {}
        self.applied = set()
        self.sequence = 0
        self.generation = 0
        self.permission_version = 0

    def fresh(self, robot, time):
        obs = self.received.get(robot)
        return (obs is not None and obs['robot_id'] == robot
                and obs['mission_revision'] == obs['map_revision'] == 1
                and all(math.isfinite(v) for v in obs['pose'] + [obs['speed'], obs['sample_time'], time])
                and 0 <= time-obs['sample_time'] <= self.params['timing']['accepted_observation_age_upper_bound']+1e-9)

    def facts(self, robot, time, core):
        obs = self.received.get(robot)
        fresh = self.fresh(robot, time)
        clear = False
        at_goal = False
        if fresh:
            x, y, angle = obs['pose']
            length, width = self.params['robot']['length'], self.params['robot']['width']
            corner_x = [x + dx*math.cos(angle)-dy*math.sin(angle)
                        for dx in (-length/2, length/2) for dy in (-width/2, width/2)]
            left, right, _, _ = self.params['map']['reservation_zone_Z']
            margin = self.params['robot']['position_error_bound'] + self.params['robot']['clearance_margin']
            clear = min(corner_x) > right+margin if robot == 'A' else max(corner_x) < left-margin
            at_goal = math.dist((x, y), self.params['map']['route_'+robot][-1]) <= .01
        robot_params = self.params['robot']
        halt = (robot_params['speed_limit']
                + robot_params['speed_error_bound']
                + robot_params['forward_acceleration_upper_bound'] * self.params['timing']['total_reaction_upper_bound']) / robot_params['braking_deceleration_lower_bound']
        return dict(ObservationUsable=fresh, PedestrianBlocked=bool(obs['blocked']) if fresh else False,
                    OwnReservation=core['owner'] == robot, Released=robot in self.released,
                    BodyClearOfZ=clear, Halted=self.intents[robot] == 'Brake' and time-self.since[robot] >= halt,
                    AtGoal=at_goal, TaskActive=True)

    def observe(self, row):
        kind, t = row['kind'], row['time']
        if kind == 'adapter':
            before = row['before']['core']
            self.core = row['after']['core']
            source = row['source']
            if source is not None:
                slot = row['before']['slot']
                permitted = before['fresh'] and not before['blocked']
                facts = dict(OwnerFree=before['owner'] is None,
                             RequestA=before['req_a'] and permitted, RequestB=before['req_b'] and permitted,
                             PreferA=slot == 'A', PreferB=slot == 'B')
                assert source['facts'] == facts
                action = language.eval_select(self.program, facts)
                assert source['raw_action'] == action
                assert row['event'][1][1] == {'SelectA': 'A', 'SelectB': 'B', 'Defer': None}[action]
            for event in row['events']:
                if event[0] == 'Observed':
                    assert event[1:] == [any(o['blocked'] for o in self.received.values()),
                                         all(self.fresh(r, t) for r in 'AB')]
                    # The explicit initial unavailable observation establishes
                    # version zero; subsequent sensor updates increment it.
                    if self.received and (before['blocked'], before['fresh']) != (event[1], event[2]):
                        self.permission_version += 1
                elif event[0] == 'Grant':
                    self.generation += 1
                elif event[0] == 'Released':
                    self.release_before[event[1]] = (t, before)
                elif event[0] == 'Issued':
                    self.issued_permissions.append((t, event[1]))
                elif event[0] == 'Proceed':
                    self.applied_permissions.append((t, event[1]))
        elif kind == 'observation_received':
            self.received[row['packet']['robot_id']] = row['packet']
        elif kind == 'complete':
            self.finish_before[row['robot']] = t
        elif kind == 'source_step':
            r = row['robot']
            before = self.release_before.get(r, (None, self.core))
            if before[0] is not None:
                assert before[0] == t
            facts = self.facts(r, t, before[1])
            assert row['facts'] == facts, ('source facts', r, t, row['facts'], facts)
            assert row['prior_mode'] == self.modes[r]
            action, nxt = language.eval_step(self.program, self.modes[r], facts)
            assert (row['raw_action'], row['raw_next']) == (action, nxt)
            self.modes[r] = nxt
            assert (r in self.release_before) == (action == 'Release')
            assert (r in self.finish_before) == (action == 'Finish')
            movement = 'Proceed' if action == 'Proceed' else 'Brake'
            if action == 'Release':
                self.release_before.pop(r)
                self.released.add(r)
                movement = self.last[r] or 'Brake'
            if action == 'Finish':
                assert self.finish_before.pop(r) == t
            assert row['physical_intent'] == movement
            self.expected_command[r] = (t, movement)
        elif kind == 'command_issued':
            c = row['command']; r = c['robot']
            assert self.expected_command[r] == (t, c['intent'])
            assert c['intent'] != self.last[r]
            assert c['scope'] == ('outside_zone_after_release' if r in self.released else 'reservation_zone')
            assert c['mission'] == 'mission-'+r and c['issued'] == t
            assert c['generation'] == self.generation and c['permission_version'] == self.permission_version
            if c['intent'] == 'Proceed' and c['scope'] == 'reservation_zone':
                self.issued_permissions.remove((t, r))
            assert c['sequence'] == self.sequence+1
            self.sequence += 1
            self.last[r] = c['intent']
            self.commands[c['sequence']] = c
        elif kind == 'command_applied':
            c = row['command']; r = c['robot']
            assert c == self.commands[c['sequence']] and c['sequence'] not in self.applied
            assert row['reservation_generation'] == self.generation
            assert row['permission_version'] == self.permission_version
            self.applied.add(c['sequence'])
            if row['current_check_verdict']:
                if c['intent'] == 'Proceed' and c['scope'] == 'reservation_zone':
                    self.applied_permissions.remove((t, r))
                if c['intent'] == 'Brake' and self.intents[r] != 'Brake':
                    self.since[r] = t
                self.intents[r] = c['intent']
            else:
                self.last[r] = None

    def finish(self):
        assert not self.release_before and not self.finish_before
        assert not self.issued_permissions and not self.applied_permissions
        assert self.applied == set(self.commands)
