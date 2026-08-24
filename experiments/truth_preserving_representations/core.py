from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product
from typing import Callable, Hashable, Iterable, Sequence

Element = Hashable


@dataclass(frozen=True)
class FiniteGroup:
    name: str
    elements: tuple[Element, ...]
    identity: Element
    operation: Callable[[Element, Element], Element]

    def multiply(self, left: Element, right: Element) -> Element:
        return self.operation(left, right)

    def power(self, value: Element, exponent: int) -> Element:
        if exponent < 0:
            raise ValueError("negative exponents are not needed by the toy apparatus")
        result = self.identity
        for _ in range(exponent):
            result = self.multiply(result, value)
        return result

    def element_order(self, value: Element) -> int:
        current = self.identity
        for exponent in range(1, len(self.elements) + 1):
            current = self.multiply(current, value)
            if current == self.identity:
                return exponent
        raise ValueError(f"could not determine order of {value!r}")

    def is_commutative(self) -> bool:
        return all(
            self.multiply(a, b) == self.multiply(b, a)
            for a in self.elements
            for b in self.elements
        )

    def has_i_like_element(self) -> bool:
        """Whether the group contains an element of order four."""
        return any(self.element_order(value) == 4 for value in self.elements)


def cyclic_group(order: int, *, name: str | None = None) -> FiniteGroup:
    if order < 1:
        raise ValueError("order must be positive")
    elements = tuple(range(order))
    return FiniteGroup(
        name=name or f"C{order}",
        elements=elements,
        identity=0,
        operation=lambda a, b: (int(a) + int(b)) % order,
    )


def klein_four_group() -> FiniteGroup:
    elements = ((0, 0), (0, 1), (1, 0), (1, 1))
    return FiniteGroup(
        name="V4",
        elements=elements,
        identity=(0, 0),
        operation=lambda a, b: ((a[0] + b[0]) % 2, (a[1] + b[1]) % 2),
    )


def dihedral_group_order_8() -> FiniteGroup:
    """D4 as pairs (rotation mod 4, reflection bit)."""
    elements = tuple((r, s) for r in range(4) for s in range(2))

    def operation(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
        r, s = a
        t, u = b
        return ((r + ((-1) ** s) * t) % 4, (s + u) % 2)

    return FiniteGroup(name="D4", elements=elements, identity=(0, 0), operation=operation)


def default_hypothesis_class() -> tuple[FiniteGroup, ...]:
    return (
        cyclic_group(4, name="C4"),
        klein_four_group(),
        cyclic_group(8, name="C8"),
        dihedral_group_order_8(),
    )


def version_space(
    groups: Iterable[FiniteGroup],
    *,
    require_i_like: bool = False,
    require_commutative: bool = False,
    carrier_order: int | None = None,
) -> tuple[str, ...]:
    survivors: list[str] = []
    for group in groups:
        if require_i_like and not group.has_i_like_element():
            continue
        if require_commutative and not group.is_commutative():
            continue
        if carrier_order is not None and len(group.elements) != carrier_order:
            continue
        survivors.append(group.name)
    return tuple(survivors)


def transported_table(
    group: FiniteGroup,
    labels: Sequence[Element],
) -> dict[Element, tuple[Element, ...]]:
    if len(labels) != len(group.elements) or len(set(labels)) != len(labels):
        raise ValueError("labels must be a bijective relabeling of the carrier")
    decode = dict(zip(labels, group.elements, strict=True))
    encode = {value: label for label, value in decode.items()}
    table: dict[Element, tuple[Element, ...]] = {}
    for left in labels:
        row = []
        for right in labels:
            product_value = group.multiply(decode[left], decode[right])
            row.append(encode[product_value])
        table[left] = tuple(row)
    return table


def transport_preserves_operation(group: FiniteGroup, labels: Sequence[Element]) -> bool:
    table = transported_table(group, labels)
    decode = dict(zip(labels, group.elements, strict=True))
    for left in labels:
        for col, right in enumerate(labels):
            coded_product = table[left][col]
            if decode[coded_product] != group.multiply(decode[left], decode[right]):
                return False
    return True


def _canonical_binary_table(table: tuple[int, ...], size: int) -> tuple[int, ...]:
    """Canonical form of a labeled binary table under all carrier permutations."""
    best: tuple[int, ...] | None = None
    for perm in permutations(range(size)):
        inverse = [0] * size
        for old, new in enumerate(perm):
            inverse[new] = old
        relabeled: list[int] = []
        for new_left in range(size):
            old_left = inverse[new_left]
            for new_right in range(size):
                old_right = inverse[new_right]
                old_out = table[old_left * size + old_right]
                relabeled.append(perm[old_out])
        candidate = tuple(relabeled)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return best


def _is_associative(table: tuple[int, ...], size: int) -> bool:
    op = lambda a, b: table[a * size + b]
    return all(
        op(op(a, b), c) == op(a, op(b, c))
        for a in range(size)
        for b in range(size)
        for c in range(size)
    )


def _has_two_sided_identity(table: tuple[int, ...], size: int) -> bool:
    op = lambda a, b: table[a * size + b]
    return any(
        all(op(e, x) == x and op(x, e) == x for x in range(size))
        for e in range(size)
    )


def count_lifts_of_c2_with_duplicate_zero() -> dict[str, int]:
    """Enumerate latent operations consistent with a non-injective decoder."""
    size = 3
    decode = (0, 0, 1)
    choices: list[tuple[int, ...]] = []
    for left in range(size):
        for right in range(size):
            target = (decode[left] + decode[right]) % 2
            choices.append(
                tuple(code for code, value in enumerate(decode) if value == target)
            )

    tables = [tuple(outputs) for outputs in product(*choices)]
    magma_classes = {_canonical_binary_table(table, size) for table in tables}

    associative = [table for table in tables if _is_associative(table, size)]
    semigroup_classes = {
        _canonical_binary_table(table, size) for table in associative
    }

    monoids = [
        table for table in associative if _has_two_sided_identity(table, size)
    ]
    monoid_classes = {_canonical_binary_table(table, size) for table in monoids}

    return {
        "labeled_lifts": len(tables),
        "magma_isomorphism_classes": len(magma_classes),
        "associative_lifts": len(associative),
        "semigroup_isomorphism_classes": len(semigroup_classes),
        "monoid_lifts": len(monoids),
        "monoid_isomorphism_classes": len(monoid_classes),
    }


def toy_report() -> dict[str, object]:
    groups = default_hypothesis_class()
    c4 = groups[0]
    labels = (37, 12, 83, 51)
    return {
        "transport_preserves_all_products": transport_preserves_operation(c4, labels),
        "transported_c4_table": transported_table(c4, labels),
        "version_space_local_i_truths": version_space(groups, require_i_like=True),
        "version_space_plus_commutativity": version_space(
            groups, require_i_like=True, require_commutative=True
        ),
        "version_space_plus_carrier_order_4": version_space(
            groups, require_i_like=True, carrier_order=4
        ),
        "noninjective_decoder": count_lifts_of_c2_with_duplicate_zero(),
    }
