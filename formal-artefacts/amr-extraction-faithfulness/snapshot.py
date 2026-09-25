"""Bind retained raw bytes to parsed syntax and actual target instructions.
This exporter is a checked engineering link, not a proved JSON/Python frontend.
"""
from dataclasses import asdict
import ast
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V2 = HERE.parent/'amr-advisory-v2'
sys.path.insert(0, str(V2))
from source_check import language, model, old

FACTS = language.SELECT_FACTS + language.STEP_FACTS + language.MODE_FACTS
ACTIONS = language.SELECT_ACTIONS + language.STEP_ACTIONS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atom(name):
    if name not in FACTS:
        raise ValueError('unapproved atom')
    return FACTS.index(name)


def expr_term(expr):
    op, *args = expr
    if op == 'const' and len(args) == 1 and type(args[0]) is bool:
        return f'(Lit {args[0]})'
    if op == 'var' and len(args) == 1:
        return f'(Atom {atom(args[0])})'
    if op == 'not' and len(args) == 1:
        return f'(BNot {expr_term(args[0])})'
    if op in ('and', 'or'):
        return '(' + ('BAnd' if op == 'and' else 'BOr') + ' [' + ','.join(map(expr_term, args)) + '])'
    raise ValueError('unknown or malformed expression')


def code_term(code):
    terms = []
    for op, *args in code:
        if op == 'PUSH' and len(args) == 1 and type(args[0]) is bool:
            terms.append(f'Push {args[0]}')
        elif op == 'LOAD' and len(args) == 1:
            terms.append(f'Load {atom(args[0])}')
        elif op == 'NOT' and not args:
            terms.append('Neg')
        elif op in ('AND', 'OR') and len(args) == 1 and type(args[0]) is int and args[0] >= 0:
            terms.append(('Conj' if op == 'AND' else 'Disj') + f' {args[0]}')
        else:
            raise ValueError('unknown or malformed instruction')
    return '[' + ','.join(terms) + ']'


def output_term(action, next_mode):
    if action not in ACTIONS or next_mode is not None and next_mode not in language.MODES:
        raise ValueError('unknown action/mode')
    nxt = 'None' if next_mode is None else f'Some {language.MODES.index(next_mode)}'
    return f'({ACTIONS.index(action)},{nxt})'


def source_observation(evaluator, *args):
    try:
        return evaluator(*args)
    except ValueError as error:
        if str(error) in ('no matching select rule', 'no matching step rule'):
            return None
        raise


def expressions():
    a, b, c = (('var', x) for x in ('OwnerFree', 'RequestA', 'RequestB'))
    n = lambda e: ('not', e)
    deep = a
    for _ in range(7):
        deep = n(deep)
    return [
        ('true', ('const', True), 'parser'), ('false', ('const', False), 'parser'),
        ('atom', a, 'parser'), ('not_atom', n(a), 'parser'),
        ('double_not', n(n(a)), 'parser'), ('triple_not', n(n(n(a))), 'parser'),
        ('not_true', n(('const', True)), 'parser'),
        ('and_two', ('and', a, b), 'parser'), ('or_three', ('or', a, b, c), 'parser'),
        ('and_three', ('and', a, b, c), 'parser'),
        ('nested', ('and', ('or', a, n(b)), n(('and', b, c))), 'parser'),
        ('repeated', ('or', a, a, n(a)), 'parser'), ('seven_nots', deep, 'parser'),
        ('empty_and', ('and',), 'constructor-only'), ('empty_or', ('or',), 'constructor-only'),
        ('unary_and', ('and', a), 'constructor-only'), ('unary_or', ('or', a), 'constructor-only'),
        ('not_empty_and', n(('and',)), 'constructor-only'),
        ('nested_empty', ('or', ('and',), ('or',)), 'constructor-only'),
    ]


def collect():
    summary_path = V2/'evidence/source/summary.json'
    summary = json.loads(summary_path.read_bytes())
    selected = summary['selected']['source_sha256']
    binding_path = HERE.parent/'amr-runtime-binding/binding.py'
    binding_tree = ast.parse(binding_path.read_text(encoding='utf-8'))
    deployed = next(ast.literal_eval(n.value) for n in binding_tree.body
                    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SOURCE_ID' for t in n.targets))
    if selected != deployed:
        raise ValueError('selected and runtime-bound source identities differ')
    samples, artifacts, seen = [], [], set()
    for sample in summary['samples']:
        path = ROOT/sample['path']
        digest = sha(path)
        if digest != sample['source_sha256']:
            raise ValueError('historical raw identity mismatch')
        samples.append(dict(sample=sample['sample_id'], path=sample['path'], sha256=digest))
        if digest in seen:
            continue
        seen.add(digest)
        program = language.parse_program(path.read_bytes().decode('utf-8'))
        target = model.extract_model(program)
        artifacts.append(dict(identity=digest, source=asdict(program), target=target.to_dict(),
                              selected=digest == selected))
    if len(samples) != 6 or len(artifacts) != 5 or selected not in seen:
        raise ValueError('unexpected retained identity domain')
    if sha(ROOT/summary['selected']['path']) != selected:
        raise ValueError('deployed bytes differ from retained source')
    deps = [Path(__file__), summary_path, binding_path, V2/'source_check.py',
            HERE.parent/'amr-forge-diagnostic/diagnostics.py']
    deps += list((HERE.parent/'amr-forge-diagnostic/profiles').rglob('*.py'))
    deps += [ROOT/s['path'] for s in samples] + [ROOT/summary['selected']['path']]
    environments = [dict(zip(FACTS, values + (False,) * (len(FACTS)-3)))
                    for values in itertools.product((False, True), repeat=3)]
    return dict(samples=samples, artifacts=artifacts, selected_source_sha256=selected,
                vocabularies=dict(facts=FACTS, actions=ACTIONS, modes=language.MODES),
                environments=environments,
                expressions=[dict(name=name, expr=expr, code=model._compile(expr), domain=domain,
                                  source_values=[language._evaluate(expr, env) for env in environments],
                                  target_values=[model._enabled(model._compile(expr), env) for env in environments])
                             for name, expr, domain in expressions()],
                input_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(deps))})


def theory(record):
    lines = ['theory AMR_Artifacts', '  imports AMR_Extraction', 'begin',
             'text \\<open>Generated concrete definitions; byte identities and frontend dependencies are in snapshot.json. No parser correctness claim.\\<close>']
    checked = []
    envs = []
    for env in record['environments']:
        branches = ' '.join(f'if a={i} then {env[fact]} else' for i, fact in enumerate(FACTS[:3]))
        envs.append('(\\<lambda>a. ' + branches + ' False)')
    lines += ['definition probe_envs :: "(nat \\<Rightarrow> bool) list" where',
              ' "probe_envs=[' + ','.join(envs) + ']"']
    for artifact in record['artifacts']:
        prefix = 'p_' + artifact['identity'][:12]
        lines.append('text \\<open>Raw SHA256 ' + artifact['identity'] + '\\<close>')
        for part in ('select', 'step'):
            source = '[' + ','.join('(' + expr_term(r['condition']) + ',' + output_term(r['action'], r['next_mode']) + ')'
                                    for r in artifact['source'][part]) + ']'
            target = '[' + ','.join('(' + code_term(r['guard']) + ',' + output_term(r['action'], r['next']) + ')'
                                    for r in artifact['target'][part]) + ']'
            name = prefix + '_' + part
            lines += [f'definition {name}_source :: "(expr \\<times> (nat \\<times> nat option)) list" where',
                      f' "{name}_source={source}"',
                      f'definition {name}_target :: "(insn list \\<times> (nat \\<times> nat option)) list" where',
                      f' "{name}_target={target}"',
                      f'lemma {name}_binding: "extract_rules {name}_source={name}_target"', ' by code_simp',
                      f'corollary {name}_preserves:',
                      f' "target_results env {name}_target=result_list (source_result env {name}_source)"',
                      f' by (simp only:{name}_binding[symmetric] extraction_preserves)']
            checked += [name+'_binding', name+'_preserves']
    for example in record['expressions']:
        name = 'expr_' + example['name']
        lines += [f'lemma {name}: "compile {expr_term(example["expr"])}={code_term(example["code"])}"',
                  ' by code_simp']
        checked.append(name)
        source_values = '[' + ','.join(str(v) for v in example['source_values']) + ']'
        target_values = '[' + ','.join('Some ['+str(v)+']' for v in example['target_values']) + ']'
        lines += [f'lemma {name}_source_values:',
                  f' "map (\\<lambda>env. eval_expr env {expr_term(example["expr"])}) probe_envs={source_values}"',
                  ' by code_simp', f'lemma {name}_target_values:',
                  f' "map (\\<lambda>env. run_code {code_term(example["code"])} env []) probe_envs={target_values}"',
                  ' by code_simp']
        checked += [name+'_source_values', name+'_target_values']
    lines += ['ML \\<open>', ' val checked = @{thms ' + ' '.join(checked) + '};',
              ' val _ = if Thm_Deps.has_skip_proof checked then error "Admitted dependency" else ();',
              ' val _ = if null (Thm_Deps.all_oracles checked) then () else error "Oracle dependency";',
              ' val audit = "Concrete bindings: no skipped proofs or oracle dependencies\\n" ^ cat_lines (map (fn th => Thm_Name.print (Thm.get_name_hint th)) checked);',
              ' val _ = Export.export @{theory} (Path.binding0 (Path.explode "artifact-audit.txt")) [XML.Text audit];',
              '\\<close>', 'end']
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    record = collect()
    text = theory(record)
    path = HERE/'hol/AMR_Artifacts.thy'
    path.write_text(text, encoding='utf-8')
    record['generated_theory_sha256'] = sha(path)
    (HERE/'evidence').mkdir(exist_ok=True)
    (HERE/'evidence/snapshot.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(dict(samples=len(record['samples']), identities=len(record['artifacts']),
                         expression_bindings=len(record['expressions']),
                         selected=record['selected_source_sha256'], generated_theory_sha256=sha(path))))
