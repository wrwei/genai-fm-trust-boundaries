"""Check the stated algebra/projection assumptions and refute the old conclusion.

An independent finite-model calculation, not an Isabelle proof. No network,
external packages, manuscript changes or implicit corpus updates.
"""
from itertools import combinations, product
import json


def audit():
    carrier = [frozenset(xs) for n in range(4)
               for xs in combinations(range(3), n)]
    zero, one = frozenset(), frozenset({0})

    def seq(x, y):
        return frozenset((a + b) % 3 for a in x for b in y)

    par = seq

    def project(x):
        return frozenset({0: 0, 1: 0, 2: 1}[a] for a in x)

    # All displayed semiring and parallel laws, not just the chosen witness.
    for x in carrier:
        assert x | zero == x and x | x == x
        assert seq(one, x) == x == seq(x, one)
        assert seq(zero, x) == zero == seq(x, zero)
        assert par(one, x) == x and par(zero, x) == zero
        for y in carrier:
            assert x | y == y | x and par(x, y) == par(y, x)
            if x <= y:
                assert project(x) <= project(y)
            for z in carrier:
                assert (x | y) | z == x | (y | z)
                assert seq(seq(x, y), z) == seq(x, seq(y, z))
                assert seq(x, y | z) == seq(x, y) | seq(x, z)
                assert seq(x | y, z) == seq(x, z) | seq(y, z)
                assert par(par(x, y), z) == par(x, par(y, z))
                assert par(x, y | z) == par(x, y) | par(x, z)
                for w in carrier:
                    assert seq(par(x, y), par(z, w)) <= par(seq(x, z), seq(y, w))

    # Even these stronger projection conditions do not repair composition.
    assert project(zero) == zero and project(one) == one
    assert all(project(x | y) == project(x) | project(y)
               for x, y in product(carrier, repeat=2))
    planner = advisory = frozenset({1})
    guard = one
    assert project(advisory) == one and guard <= one
    lhs = project(seq(par(planner, advisory), guard))
    rhs = project(planner)
    assert not lhs <= rhs, "The old authority claim must fail in this model"

    assert all(seq(x, t) <= x for x, t in product(carrier, repeat=2) if t <= one)
    assert all(project(seq(par(p, d), zero)) <= project(p)
               for p, d in product(carrier, repeat=2))
    # The missing equation is separately exposed.
    assert project(par(planner, advisory)) != par(project(planner), project(advisory))
    return {
        "carrier": "powerset of the additive monoid Z/3Z",
        "carrier_size": len(carrier),
        "addition_and_order": "union and subset",
        "sequential_and_parallel": "setwise addition modulo 3",
        "algebraic_zero": [], "algebraic_unit": [0],
        "projection_element_map": {"0": 0, "1": 0, "2": 1},
        "semiring_parallel_exchange_laws": "passed exhaustively",
        "projection_monotone_zero_unit_union": "passed exhaustively",
        "witness": {"planner": [1], "advisory": [1], "guard": [0],
                    "premises_hold": True, "lhs": sorted(lhs), "rhs": sorted(rhs),
                    "conclusion_holds": False},
        "two_basic_lemmas_in_this_model": "passed",
        "scope": "Refutes the old displayed assumptions as sufficient; not CKA itself, not an Isabelle run.",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
