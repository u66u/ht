from typing import Any, Callable, TypeVar, Generic, Protocol
from abc import ABC, abstractmethod


T = TypeVar("T", bound=Type)
U = TypeVar("U", bound=Type)

A = TypeVar("A", bound=Type)
B = TypeVar("B", bound=Type)
C = TypeVar("C", bound=Type)


class Term(ABC):
    pass


class Type(Term):
    pass


class Path(Generic[A], Type):
    def __init__(self, A: Type, x: Term, y: Term):
        self.A = A
        self.x = x
        self.y = y

def refl(A: Type, a: Term) -> Path[A]:
    return Path(A, a, a)

def J(A: Type, C: Callable[[Term, Term, Path], Type], 
      d: Callable[[Term], Term], 
      x: Term, y: Term, p: Path[A]) -> Term:
    raise NotImplementedError("J eliminator not fully implemented")

def sym(A: Type, x: Term, y: Term, p: Path[A]) -> Path[A]:
    def C(_x: Term, _y: Term, _p: Path[A]) -> Type:
        return Path(A, _y, _x)
    return J(A, C, lambda z: refl(A, z), x, y, p)

def trans(A: Type, x: Term, y: Term, z: Term, p: Path[A], q: Path[A]) -> Path[A]:
    def C(_y: Term, _: Path[A]) -> Type:
        return Path(A, x, _y)
    return J(A, C, lambda _: p, y, z, q)


class Unit(Type):
    star: Term = object()  # A single inhabitant of Unit

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Unit)


class DependentType(Protocol[A]):
    def __call__(self, x: A, p: Path[A]) -> Type: ...


class Bool(Type):
    true: Term = object()
    false: Term = object()

    def __init__(self, value: bool):
        self.value = self.true if value else self.false

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Bool) and self.value is other.value

    def __bool__(self):
        return self.value is self.true


class Function(Type):
    def __init__(self, domain: Type, codomain: Type, impl: Callable[[Any], Any]):
        self.domain = domain
        self.codomain = codomain
        self.impl = impl

    def __call__(self, x: Term) -> Type:
        return self.codomain(x)


    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Function):
            return False
        return self.domain == other.domain and self.codomain == other.codomain


class Pi(Type, Generic[A, B]):
    def __init__(self, domain: Type, codomain: Callable[[Term], Type]):
        self.domain = domain
        self.codomain = codomain

    def __call__(self, x: Any) -> B:
        return self.codomain(x)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Pi)
            and self.domain == other.domain
            and all(self.codomain(x) == other.codomain(x) for x in self.domain)  # TODO
        )


class DependentFunction(Term):
    def __init__(self, pi_type: Pi, impl: Callable[[Term], Term]):
        self.pi_type = pi_type
        self.impl = impl

    def __call__(self, x: Term) -> Term:
        return self.impl(x)

    def dependent_apply(f: DependentFunction, x: Term) -> Term:
        return f(x)


class Identity(Type):
    def __init__(self, A: Type, x: Any, y: Any):
        self.A = A
        self.x = x
        self.y = y

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Identity):
            return False
        return self.A == other.A and self.x == other.x and self.y == other.y


class QuasiInverse:
    def __init__(
        self,
        f: Function,
        g: Function,
        eta: Callable[[Any], Identity],
        epsilon: Callable[[Any], Identity],
    ):
        self.f = f
        self.g = g
        self.eta = eta
        self.epsilon = epsilon


class Equivalence(Type):
    def __init__(self, A: Type, B: Type, quasi_inverse: QuasiInverse):
        self.A = A
        self.B = B
        self.quasi_inverse = quasi_inverse

    def to_path(self) -> Path:
        return Path(self.A, self.B)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Equivalence):
            return False
        return (
            self.A == other.A
            and self.B == other.B
            and self.quasi_inverse.f == other.quasi_inverse.f
            and self.quasi_inverse.g == other.quasi_inverse.g
        )



def ap(f: Callable[[A], B], p: Path[A]) -> Path[B]:
    return Path(f(p.source), f(p.target))


def id_function(A: Type) -> Function:
    return Function(A, A, lambda x: x)


def compose_functions(f: Function, g: Function) -> Function:
    if f.codomain != g.domain:
        raise ValueError("Functions are not composable")
    return Function(f.domain, g.codomain, lambda x: g(f(x)))

def lambda_abstraction(A: Type, f: Callable[[Term], Term]) -> Term:
    return f  # siimplified, we'd need to handle scope and evaluation

def apply(f: Term, x: Term) -> Term:
    return f(x)  # simplification