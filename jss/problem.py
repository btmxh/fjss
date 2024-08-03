from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable, Iterator, KeysView
from random import expovariate, randint, choices
from typing import override
from statistics import median
import json

Time = float


class Operation:
    processing_times: dict[int, Time]
    name: str

    def __init__(self, name: str, processing_times: dict[int, Time]):
        self.name = name
        self.processing_times = dict(processing_times)

    def get_machines(self) -> KeysView[int]:
        return self.processing_times.keys()

    def get_processing_time(self, machine: int) -> Time:
        return self.processing_times[machine]


class Job:
    name: str
    arrival_time: Time
    operations: list[Operation]
    weight: float

    median_work_time: list[Time]
    median_work_remaining: list[Time]
    last_operation_ready_time: Time

    def __init__(self, name: str, arrival_time: Time, operations: list[Operation]):
        self.name = name
        self.arrival_time = arrival_time
        self.operations = list(operations)
        self.weight = 1.0

        self.median_work_time = []
        self.median_work_remaining = []
        self.last_operation_ready_time = Time(0)
        cur_median_work_remaining = Time(0)

        for op in reversed(operations):
            cur_median_work_time = median(op.processing_times.values())
            cur_median_work_remaining += cur_median_work_time
            self.median_work_remaining.append(cur_median_work_remaining)
            self.median_work_time.append(cur_median_work_time)

    def update_ready_time(self, new_ready_time: Time):
        self.last_operation_ready_time = new_ready_time


class FJSS(ABC):
    num_machines: int

    def __init__(self, num_machines: int) -> None:
        self.num_machines = num_machines

    @abstractmethod
    def generate_jobs(self) -> Generator[Job, None, None]: ...


class StaticFJSS(FJSS):
    name: str
    jobs: list[Job]
    lower_bound: Time | None

    def __init__(
        self,
        name: str,
        num_machines: int,
        jobs: list[Job],
        lower_bound: Time | None = None,
    ) -> None:
        super().__init__(num_machines)
        self.name = name
        self.jobs = list(jobs)
        self.lower_bound = lower_bound

    @staticmethod
    def load(
        path: str, name: str | None = None, lower_bound: Time | None = None
    ) -> "StaticFJSS":
        name = name or path
        jobs: list[Job] = []
        with open(path, "r") as f:
            num_jobs, num_machines = list(map(int, f.readline().split()[:2]))
            for i in range(num_jobs):
                nums = list(map(int, f.readline().split()))
                nums.reverse()
                num_ops = nums.pop()

                operations: list[Operation] = []

                for j in range(num_ops):
                    num_processable_machines = nums.pop()
                    processing_times: dict[int, Time] = {}
                    for _ in range(num_processable_machines):
                        index = nums.pop()
                        time = Time(nums.pop())
                        processing_times[index] = time
                    op = Operation(f"{i + 1}:{j + 1}", processing_times)
                    operations.append(op)

                job = Job(f"{i + 1}", Time(0), operations)
                jobs.append(job)

            # shorten path
            return StaticFJSS(name, num_machines, jobs, lower_bound)

    @override
    def generate_jobs(self) -> Generator[Job, None, None]:
        yield from self.jobs


class DynamicFJSS(FJSS):
    num_jobs: int
    utilization_rate: float

    def __init__(self, num_machines: int, num_jobs: int, utilization_rate: float):
        super().__init__(num_machines)
        self.num_jobs = num_jobs
        self.utilization_rate = utilization_rate

    def random_job(self, name: str, arrival_time: Time) -> Job:
        operations: list[Operation] = []
        for i in range(randint(1, 10)):
            processing_times: dict[int, Time] = {}
            for machine in choices(
                list(range(self.num_machines)), k=randint(1, self.num_machines)
            ):
                processing_times[machine] = Time(randint(1, 99))
            operations.append(Operation(f"{name}:{i + 1}", processing_times))
        return Job(name, arrival_time, operations)

    @override
    def generate_jobs(self) -> Generator[Job, None, None]:
        time = Time(0.0)
        for i in range(self.num_jobs):
            time += Time(expovariate(self.utilization_rate))
            yield self.random_job(f"{i + 1}", time)


FJSP_INSTANCES: dict[str, StaticFJSS] = {}

with open("./fjsp-instances/instances.json") as f:
    for instance in json.load(f):
        path: str = instance["path"]
        lower_bound: Time | None = instance["optimum"]
        if lower_bound is None:
            lower_bound = instance["bounds"]["lower"]
        assert lower_bound is not None
        problem = StaticFJSS.load("./fjsp-instances/" + path, path, lower_bound)
        FJSP_INSTANCES[path] = problem


class StaticFJSSSet(Iterable[StaticFJSS]):
    problems: list[StaticFJSS]

    def __init__(self, prefix: str):
        self.problems = [
            problem
            for path, problem in FJSP_INSTANCES.items()
            if path.startswith(prefix)
        ]

    def __len__(self) -> int:
        return len(self.problems)

    @override
    def __iter__(self) -> Iterator[StaticFJSS]:
        return iter(self.problems)


if __name__ == "__main__":
    sfjss = StaticFJSS.load("./fjsp-instances/barnes/mt10x.txt")
    assert sfjss.num_machines == 11
    assert len(sfjss.jobs) == 10
    assert len(sfjss.jobs[0].operations[0].processing_times) == 1

    dfjss = DynamicFJSS(10, 100, 0.8)
    assert dfjss.num_machines == 10
    jobs = list(dfjss.generate_jobs())

    assert len(StaticFJSSSet("barnes").problems) == 21
