"""Serial fixed-mission adapter; provider bytes have no control entry point."""
from dataclasses import asdict
import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
V2 = HERE.parent / 'amr-advisory-v2'
sys.path.insert(0, str(V2))
from advice_mailbox import AdviceMailbox, parse_advice
from protocol import Core, SourceController, step, reference_accepts
SOURCE_ID = '9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd'


class Runtime:
    def __init__(self, request_id, context_id, *, source=None):
        if any(type(v) is not str or not v for v in (request_id, context_id)):
            raise ValueError('fixed nonempty string identities required')
        self.box = AdviceMailbox(request_id, context_id)
        self.requested = False
        self.core = Core()
        self.source = source if source is not None else SourceController.from_selected()
        if (type(self.source) is not SourceController or self.source.identity != SOURCE_ID
                or hashlib.sha256(self.source.raw).hexdigest() != SOURCE_ID):
            raise ValueError('only the frozen accepted SourceController may be reused')

    def snapshot(self):
        return dict(core=asdict(self.core), requested=self.requested, slot=self.box.advice)

    def receive(self, request_id, context_id, text):
        before = self.snapshot()
        # Decode the event independently of slot occupancy: duplicate Provider
        # values remain visible to the causal model but cannot overwrite its slot.
        matching = ((request_id, context_id) == (self.box.request_id, self.box.context_id))
        parsed = None
        if matching:
            try:
                parsed = parse_advice(text)
            except (ValueError, TypeError, UnicodeError, RecursionError):
                pass
        verdict = (self.box.receive(request_id, context_id, text) if self.requested
                   else 'not_requested')
        return dict(before=before, after=self.snapshot(), event=['Provider', parsed],
                    raw_input=['Message', request_id, context_id, text],
                    events=[], verdict=verdict, source=None)

    def local(self, inp):
        raw_input = list(inp)
        op, *args = inp
        arity = {'Register': 1, 'Observe': 2, 'Validate': 0, 'Service': 0,
                 'Commit': 0, 'Issue': 1, 'Apply': 0, 'Release': 2,
                 'RequestAdvice': 0, 'Consume': 0}
        if op not in arity or len(args) != arity[op]:
            raise ValueError('trusted interface has no externally supplied selection')
        before = self.snapshot()
        decision = None
        if op in ('Validate', 'Service'):
            # Pending is already a source-chosen intent, never a permission.
            intent = None
            if self.core.pending is None:
                latch = self.box.latch()
                intent, decision = self.source.select(self.core, latch['advice'])
                decision = dict(decision, latch=latch)
            inp = (op, intent)
        elif op == 'Consume':
            inp = (op, self.box.advice)
        next_core, events = step(self.core, inp)
        if not reference_accepts(self.core, events):
            raise RuntimeError('reference authority violation')
        self.core = next_core
        if op == 'RequestAdvice':
            self.requested = True
        return dict(before=before, after=self.snapshot(), event=['Trusted', list(inp), events],
                    raw_input=raw_input, events=events, source=decision)
