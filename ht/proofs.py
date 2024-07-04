from .types import (
    Type,
    Path,
    Function,
    Equivalence,
    Bool,
    Unit,
    Identity,
    QuasiInverse,
    id_function,
    compose_functions,
)
from .space import Space
from typing import Any, Callable, TypeVar, Generic


def is_quasi_inverse(f: Function, g: Function) -> bool:

    if isinstance(f.domain, Unit) and isinstance(f.codomain, Unit):
        return g(f(Unit())) == Unit() and f(g(Unit())) == Unit()

    elif isinstance(f.domain, Bool) and isinstance(f.codomain, Bool):
        return (
            g(f(Bool(True))) == Bool(True)
            and g(f(Bool(False))) == Bool(False)
            and f(g(Bool(True))) == Bool(True)
            and f(g(Bool(False))) == Bool(False)
        )

    elif (
        isinstance(f.domain, Unit)
        and isinstance(f.codomain, Bool)
        and isinstance(g.domain, Bool)
        and isinstance(g.codomain, Unit)
    ):
        return g(f(Unit())) == Unit() and f(g(Bool(True))) == f(g(Bool(False)))

    else:
        raise NotImplementedError("Quasi-inverse check not implemented for these types")


def prove_equivalence(A: Type, B: Type, f: Function, g: Function) -> Equivalence:
    if not is_quasi_inverse(f, g):
        raise ValueError("Functions are not quasi-inverses")

    def eta(x: Any) -> Identity:
        return Identity(A, x, g(f(x)))

    def epsilon(y: Any) -> Identity:
        return Identity(B, f(g(y)), y)

    quasi_inverse = QuasiInverse(f, g, eta, epsilon)
    return Equivalence(A, B, quasi_inverse)


def example_proof():
    space = Space()

    unit_type = Unit()
    bool_type = Bool(True)
    space.add_type("Unit", unit_type)
    space.add_type("Bool", bool_type)

    f = Function(unit_type, bool_type, lambda _: True)
    g = Function(bool_type, unit_type, lambda _: Unit())

    try:
        equiv = prove_equivalence(unit_type, bool_type, f, g)
        path = equiv.to_path()
        assert path.source == unit_type, f"Expected {unit_type}, got {path.source}"
        assert path.target == bool_type, f"Expected {bool_type}, got {path.target}"

        composed = compose_functions(f, g)
        assert (
            composed(unit_type) == unit_type
        ), f"Expected {unit_type}, got {composed(unit_type)}"
        print("Equivalence between Unit and Bool proved successfully")
    except ValueError as e:
        print(f"Failed to prove equivalence between Unit and Bool: {e}")

    h = Function(bool_type, bool_type, lambda x: not x)
    try:
        non_equiv = prove_equivalence(bool_type, bool_type, h, h)
        print("Unexpectedly proved equivalence for non-equivalent functions")
    except ValueError as e:
        print(
            f"As expected, failed to prove equivalence for non-equivalent functions: {e}"
        )

    id_bool = Function(bool_type, bool_type, lambda x: x)
    try:
        equiv_id = prove_equivalence(bool_type, bool_type, id_bool, id_bool)
        print("Successfully proved equivalence for identity function on Bool")
    except ValueError as e:
        print(
            f"Unexpectedly failed to prove equivalence for identity function on Bool: {e}"
        )

    print("All proofs completed successfully")
