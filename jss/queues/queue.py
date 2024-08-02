from abc import abstractmethod


class Queue[T]:
    @abstractmethod
    def push(self, value: T): ...

    @abstractmethod
    def pop(self) -> T | None: ...

    @abstractmethod
    def __len__(self) -> int: ...
