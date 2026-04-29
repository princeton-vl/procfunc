from procfunc.transpiler.identifiers import dedup_names_with_suffix


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
