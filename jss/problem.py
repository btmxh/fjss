from abc import abstractmethod
from collections.abc import Generator, KeysView
from random import expovariate, randint, choices
from typing import override

Time = float


class Operation:
    processing_times: dict[int, Time]
    name: str

    def __init__(self, name: str, processing_times: dict[int, Time]):
        self.name = name
        self.processing_times = dict(processing_times)

    def get_machines(self) -> KeysView[int]:
        return self.processing_times.keys()

    def get_processing_time(self, machine: int) -> Time | None:
        return self.processing_times.get(machine, None)


class Job:
    name: str
    arrival_time: Time
    operations: list[Operation]

    def __init__(self, name: str, arrival_time: Time, operations: list[Operation]):
        self.name = name
        self.arrival_time = arrival_time
        self.operations = list(operations)


class FJSS:
    num_machines: int

    def __init__(self, num_machines: int) -> None:
        self.num_machines = num_machines

    @abstractmethod
    def generate_jobs(self) -> Generator[Job, None, None]: ...


class StaticFJSS(FJSS):
    jobs: list[Job]

    def __init__(self, num_machines: int, jobs: list[Job]) -> None:
        super().__init__(num_machines)
        self.jobs = list(jobs)

    @staticmethod
    def load(path: str) -> "StaticFJSS":
        jobs: list[Job] = []
        with open(path, "r") as f:
            num_jobs, num_machines = list(map(int, f.readline().split()))[:2]
            for i in range(num_jobs):
                nums = list(map(int, f.readline().split()))
                nums.reverse()
                num_ops = nums.pop()

                operations: list[Operation] = []

                for j in range(num_ops):
                    num_processable_machines = nums.pop()
                    processing_times: dict[int, Time] = {}
                    for _ in range(num_processable_machines):
                        index = nums.pop() - 1
                        time = Time(nums.pop())
                        processing_times[index] = time
                    op = Operation(f"{i + 1}:{j + 1}", processing_times)
                    operations.append(op)

                job = Job(f"{i + 1}", Time(0), operations)
                jobs.append(job)
            return StaticFJSS(num_machines, jobs)


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


if __name__ == "__main__":
    sfjss = StaticFJSS.load("./dataset/Monaldo/Fjsp/Job_Data/Barnes/Text/mt10x.fjs")
    assert sfjss.num_machines == 11
    assert len(sfjss.jobs) == 10
    assert len(sfjss.jobs[0].operations[0].processing_times) == 1

    dfjss = DynamicFJSS(10, 100, 0.8)
    assert dfjss.num_machines == 10
    jobs = list(dfjss.generate_jobs())
    print(jobs[-1].arrival_time)
