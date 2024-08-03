from collections import deque
from typing import override

from fjss.queues.queue import Queue


class FIFOQueue[T](Queue[T]):
    queue: deque[T]

    def __init__(self) -> None:
        super().__init__()
        self.queue = deque()

    @override
    def push(self, value: T):
        self.queue.append(value)

    @override
    def pop(self) -> T | None:
        try:
            return self.queue.popleft()
        except IndexError:
            return None

    @override
    def __len__(self) -> int:
        return len(self.queue)
