from typing import Any, Callable, TypeVar, Generic, Protocol
from abc import ABC, abstractmethod


class Type(ABC):
    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass


class Unit(Type):
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Unit)


class Bool(Type):
    def __init__(self, value: bool):
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Bool) and self.value == other.value

    def __call__(self):
        return self.value

    def __bool__(self):
        return self.value


class Function(Type):
    def __init__(self, domain: Type, codomain: Type, impl: Callable[[Any], Any]):
        self.domain = domain
        self.codomain = codomain
        self.impl = impl

    def __call__(self, x: Any) -> Any:
        if isinstance(x, Bool):
            return Bool(self.impl(x.value))
        return self.impl(x)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Function):
            return False
        return self.domain == other.domain and self.codomain == other.codomain


class Identity(Type):
    def __init__(self, A: Type, x: Any, y: Any):
        self.A = A
        self.x = x
        self.y = y

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Identity):
            return False
        return self.A == other.A and self.x == other.x and self.y == other.y


T = TypeVar("T", bound=Type)
U = TypeVar("U", bound=Type)

A = TypeVar("A", bound=Type)
B = TypeVar("B", bound=Type)
C = TypeVar("C", bound=Type)


class Path(Generic[A]):
    def __init__(self, source: A, target: A):
        self.source = source
        self.target = target

    # return A or Path or Path[A] ?
    @staticmethod
    def refl(a: A) -> A:
        return Path(a, a)

    def sym(self) -> A:
        return Path(self.target, self.source)

    def trans(self, other: A) -> A:
        if self.target != other.source:
            raise ValueError("Paths are not composable")
        return Path(self.source, other.target)


class DependentType(Protocol[A]):
    def __call__(self, x: A, p: Path[A]) -> Type: ...


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


class Pi(Type, Generic[A, B]):
    def __init__(self, domain: A, codomain: Callable[[Any], B]):
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


def J(A: Type, a: A, C: DependentType[A], d: Any, x: A, p: Path[A]) -> Any:
    if p.source == p.target == a:
        return d
    else:
        # In a real implementation, we would recurse on the structure of the path
        raise NotImplementedError("J eliminator not fully implemented")


def ap(f: Callable[[A], B], p: Path[A]) -> Path[B]:
    return Path(f(p.source), f(p.target))


def id_function(A: Type) -> Function:
    return Function(A, A, lambda x: x)


def compose_functions(f: Function, g: Function) -> Function:
    if f.codomain != g.domain:
        raise ValueError("Functions are not composable")
    return Function(f.domain, g.codomain, lambda x: g(f(x)))
