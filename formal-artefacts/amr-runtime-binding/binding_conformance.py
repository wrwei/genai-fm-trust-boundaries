"""Full finite adapter comparison with a table computed by Isabelle, not Python."""
from dataclasses import asdict
import hashlib
import itertools
import json
from pathlib import Path
from binding import Runtime, Core, HERE, V2, SourceController, parse_advice
from conformance import states, encode_state, encode_events

ROBOTS = (None, 'A', 'B')
TABLE = HERE/'hol/export/AMR_Runtime_Binding.AMR_Runtime_Binding/binding.csv'


def raw_inputs():
    return ([('Register', r) for r in 'AB']
            + [('Observe', b, f) for b, f in itertools.product((False, True), repeat=2)]
            + [('Validate',), ('Service',), ('Commit',)]
            + [('Issue', r) for r in 'AB'] + [('Apply',)]
            + [('Release', r, c) for r in 'AB' for c in (False, True)]
            + [('RequestAdvice',), ('Consume',)]
            + [('Message', a, b, r) for a, b, r in
               itertools.product((False, True), (False, True), ROBOTS)])


def encode_snapshot(snapshot):
    return encode_state(Core(**snapshot['core'])) + [int(snapshot['requested']), ROBOTS.index(snapshot['slot'])]


def encode_event(event):
    if event[0] == 'Provider':
        return [1, ROBOTS.index(event[1]), 0, 0, 0, 0, 0]
    _, inp, events = event
    op, *args = inp
    tag = ['Register', 'Observe', 'Validate', 'Commit', 'Issue', 'Apply',
           'Release', 'Service', 'RequestAdvice', 'Reply', 'Consume'].index(op) + 1
    values = [0, 0]
    if op == 'Observe':
        values = [int(v) for v in args]
    elif args:
        values[0] = ROBOTS.index(args[0])
        if op == 'Release':
            values[1] = int(args[1])
    return [2, tag] + values + encode_events(events)


def encode_row(row):
    return encode_snapshot(row['before']) + encode_snapshot(row['after']) + encode_event(row['event'])


def classify(inp):
    if inp[0] != 'Message':
        return tuple(inp)
    _, req, ctx, text = inp
    try:
        value = parse_advice(text)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        value = None
    return ('Message', req == 'req', ctx == 'ctx', value)


class HOLTable:
    def __init__(self):
        self.rows = [[int(v) for v in line.split(',')] for line in TABLE.read_text().splitlines()]
        if len(self.rows) != 77760:
            raise ValueError('expected exactly 432 x 6 x 30 HOL rows')
        self.state_index = {tuple(encode_state(s)): i for i, s in enumerate(states())}
        self.input_index = {inp: i for i, inp in enumerate(raw_inputs())}

    def expected(self, before, inp):
        n = self.state_index[tuple(encode_state(Core(**before['core'])))]
        n = n * 6 + int(before['requested']) * 3 + ROBOTS.index(before['slot'])
        return self.rows[n * 30 + self.input_index[tuple(inp)]]

    def check(self, row):
        return encode_row(row) == self.expected(row['before'], classify(row['raw_input']))


def check_finite():
    table = HOLTable()
    source = SourceController.from_selected()
    failures = []
    n = 0
    for s in states():
        for requested, slot in itertools.product((False, True), ROBOTS):
            for inp in raw_inputs():
                rt = Runtime('req', 'ctx', source=source)
                rt.core, rt.requested, rt.box.advice = s, requested, slot
                if inp[0] == 'Message':
                    _, a, b, value = inp
                    row = rt.receive('req' if a else 'wrong', 'ctx' if b else 'wrong',
                                     'invalid' if value is None else json.dumps({'prefer': value}))
                else:
                    row = rt.local(inp)
                if encode_row(row) != table.rows[n]:
                    failures.append(dict(index=n, input=inp, expected=table.rows[n], observed=encode_row(row)))
                n += 1
    return dict(rows=n, mismatch_count=len(failures), examples=failures[:20], source_id=source.identity,
                table_sha256=hashlib.sha256(TABLE.read_bytes()).hexdigest(),
                scope='finite equality classes and parsed values; not a proof of Python or JSON parsing')


# Expectations are frozen literals, not derived by reusing parse_advice.
PARSER_CASES = [
    ('A', '{"prefer":"A"}', 'A'), ('B', '{"prefer":"B"}', 'B'),
    ('space', ' \n { "prefer" : "B" }\t', 'B'),
    ('escaped_key', '{"pr\\u0065fer":"B"}', 'B'),
    ('escaped_value', '{"prefer":"\\u0042"}', 'B'),
    ('limit_1024', '{"prefer":"B"}' + ' ' * 1010, 'B'),
    ('limit_1025', '{"prefer":"B"}' + ' ' * 1011, None),
    ('empty', '', None), ('word', 'B', None), ('truncated', '{"prefer":', None),
    ('unknown', '{"prefer":"C"}', None), ('extra', '{"prefer":"B","grant":true}', None),
    ('duplicate', '{"prefer":"A","prefer":"B"}', None),
    ('escaped_duplicate', '{"prefer":"A","pr\\u0065fer":"B"}', None),
    ('array', '[{"prefer":"B"}]', None), ('null', 'null', None),
    ('bool', '{"prefer":true}', None), ('number', '{"prefer":1}', None),
    ('nested', '{"prefer":{"prefer":"B"}}', None), ('nonascii', '{"prefer":"乙"}', None),
    ('nan', '{"prefer":NaN}', None), ('bytes', b'{"prefer":"B"}', None),
    ('surrogate', '\ud800', None), ('deep', '[' * 500 + '0' + ']' * 500, None),
]


def check_parser():
    results = []
    for name, payload, expected in PARSER_CASES:
        try:
            actual = parse_advice(payload)
        except (ValueError, TypeError, UnicodeError, RecursionError):
            actual = None
        results.append(dict(name=name, expected=expected, actual=actual, passed=actual == expected))
    return results


if __name__ == '__main__':
    report = dict(finite=check_finite(), parser=check_parser())
    report['passed'] = report['finite']['mismatch_count'] == 0 and all(r['passed'] for r in report['parser'])
    (HERE/'evidence').mkdir(exist_ok=True)
    (HERE/'evidence/conformance.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))
    raise SystemExit(0 if report['passed'] else 1)
