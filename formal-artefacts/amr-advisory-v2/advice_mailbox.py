"""Bounded data parsing and trusted request binding; never selects a robot."""
import json


def _unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('duplicate key')
        result[key]=value
    return result


def parse_advice(text):
    if type(text) is not str or len(text.encode('utf-8'))>1024:
        raise ValueError('invalid advice payload')
    data=json.loads(text,object_pairs_hook=_unique)
    if type(data) is not dict or set(data)!={'prefer'} or data['prefer'] not in ('A','B'):
        raise ValueError('exact A/B advice object required')
    return data['prefer']


class AdviceMailbox:
    def __init__(self,request_id,context_id):
        if not request_id or not context_id:
            raise ValueError('trusted request/context identities required')
        self.request_id=request_id
        self.context_id=context_id
        self.advice=None
        self.latches=0

    def receive(self,request_id,context_id,text):
        if (request_id,context_id)!=(self.request_id,self.context_id):
            return 'wrong_binding'
        if self.advice is not None:
            return 'duplicate_ignored'
        try:
            advice=parse_advice(text)
        except (ValueError,TypeError,UnicodeError,RecursionError):
            return 'invalid_payload'
        self.advice=advice
        return 'accepted'

    def latch(self):
        self.latches+=1
        return dict(decision_id=self.latches,advice=self.advice,request_id=self.request_id,
                    context_id=self.context_id,reason='valid_advice' if self.advice else 'no_valid_advice')
