from typing import Callable, Protocol, Self, cast, override
from collections.abc import Iterable
from jss.queues.queue import Queue


class Comparable(Protocol):
    def __lt__(self, value: Self, /) -> bool: ...


class DynamicPriorityQueue[T, K: Comparable](Queue[T]):
    values: list[T]
    key_fn: Callable[[T], K]

    def __init__(
        self,
        lst: Iterable[T] = [],
        key_fn: Callable[[T], K] = lambda value: cast(K, value),
    ) -> None:
        super().__init__()
        self.key_fn = key_fn
        self.values = list(lst)

    @override
    def push(self, value: T):
        self.values.append(value)

    @override
    def pop(self) -> T | None:
        if len(self) == 0:
            return None
        i = min(range(len(self)), key=lambda i: self.key_fn(self.values[i]))
        self.values[i], self.values[-1] = self.values[-1], self.values[i]
        return self.values.pop()

    @override
    def __len__(self) -> int:
        return len(self.values)
