from abc import ABC, abstractmethod


class Queue[T](ABC):
    @abstractmethod
    def push(self, value: T): ...

    @abstractmethod
    def pop(self) -> T | None: ...

    @abstractmethod
    def __len__(self) -> int: ...
