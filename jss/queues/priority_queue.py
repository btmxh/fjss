from heapq import heapify, heappush, heappop
from typing import Callable, Protocol, Self, cast, override
from collections.abc import Iterable
from jss.queues.queue import Queue


class Comparable(Protocol):
    def __lt__(self, value: Self, /) -> bool: ...


class PriorityQueue[T, K: Comparable](Queue[T]):
    heap: list[tuple[K, int, T]]
    counter: int
    key_fn: Callable[[T], K]

    def __init__(
        self,
        lst: Iterable[T],
        key_fn: Callable[[T], K] = lambda value: cast(K, value),
    ) -> None:
        super().__init__()
        self.counter = 0
        self.key_fn = key_fn
        self.heap = [self.make_element(value) for value in lst]
        heapify(self.heap)

    def make_element(self, value: T) -> tuple[K, int, T]:
        self.counter += 1
        return (self.key_fn(value), self.counter, value)

    @override
    def push(self, value: T):
        heappush(self.heap, self.make_element(value))

    @override
    def pop(self) -> T | None:
        try:
            return heappop(self.heap)[2]
        except IndexError:
            return None

    @override
    def __len__(self) -> int:
        return len(self.heap)

    def to_sorted_list(self) -> list[T]:
        """
        warning: this clears the list completely
        """
        lst: list[T] = []
        while True:
            elem = self.pop()
            if elem is None:
                break
            lst.append(elem)
        return lst


if __name__ == "__main__":
    pq: PriorityQueue[int, int] = PriorityQueue([4, 3, 2, 1])
    pq.push(100)
    pq.push(300)
    pq.push(200)
    assert pq.to_sorted_list() == [1, 2, 3, 4, 100, 200, 300]

    pq = PriorityQueue([4, 3, 2, 1], key_fn=lambda x: -x)
    pq.push(100)
    pq.push(300)
    pq.push(200)
    assert pq.to_sorted_list() == [300, 200, 100, 4, 3, 2, 1]
