from ht import Bool, Function, Path, J


def test_J():
    b_true = Bool(True)
    b_false = Bool(False)
    p = Path(b_true, b_false)

    def C(x: Bool, _: Path[Bool]) -> Type:
        return Bool

    d = b_true

    result = J(Bool, b_true, C, d, b_false, p)

    assert result == d, f"Expected {d}, got {result}"

    print("J test passed successfully")


test_J()
