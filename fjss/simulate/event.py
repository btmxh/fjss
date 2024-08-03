from typing import override
from fjss.problem import Job, Time
from abc import ABC, abstractmethod


class SimulationEvent(ABC):
    @abstractmethod
    def arrival_time(self) -> Time: ...


class NewJobEvent(SimulationEvent):
    job: Job

    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job

    @override
    def arrival_time(self) -> Time:
        return self.job.arrival_time


class MachineFinishEvent(SimulationEvent):
    time: Time
    machine: int
    job: Job
    operation_index: int

    def __init__(self, time: Time, machine: int, job: Job, operation_index: int):
        super().__init__()
        self.time = time
        self.machine = machine
        self.job = job
        self.operation_index = operation_index

    @override
    def arrival_time(self) -> Time:
        return self.time
