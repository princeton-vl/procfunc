import numpy as np

import procfunc as pf
from procfunc.codegen import codegen
from procfunc.codegen.identifiers import dedup_names_with_suffix


def _codegen_and_call(func, **inputs):
    graph = pf.trace(func)
    src = codegen.to_python(graph, toplevel_as_maincall=False)
    namespace = {}
    exec(src, namespace)  # noqa: S102
    return src, namespace[func.__name__](**inputs)


def test_folded_operand_ending_in_call_keeps_parens():
    def sub_of_add_astype(a, b, c):
        return c - (a + b.astype(float))

    src, result = _codegen_and_call(
        sub_of_add_astype, a=np.float64(1.0), b=np.float64(2.0), c=np.float64(10.0)
    )
    assert "c - (a + b.astype(float))" in src, src
    assert result == 7.0


def test_negative_constant_pow_base_keeps_parens():
    def pow_negative_base(x):
        return (-2.0) ** x

    src, result = _codegen_and_call(pow_negative_base, x=2.0)
    assert "(-2.0) ** x" in src, src
    assert result == 4.0


def test_dedup_suffix_collides_with_later_base_name():
    names = {
        0: "a_1",  # strips to 'a'
        1: "a_2",  # strips to 'a'
        2: "a_0_3",  # strips to 'a_0'
    }
    result = dedup_names_with_suffix(
        names,
        separator="_",
        order=[0, 1, 2],
        first_use_suffix=True,
    )
    print(f"{result=}")
    values = list(result.values())
    assert len(values) == len(set(values)), f"Duplicate names in {values}"
