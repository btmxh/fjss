from typing import Callable, Self, override
from os import getenv
from jss.problem import FJSS, Job, Operation, Time
from jss.queues.priority_queue import PriorityQueue
from jss.queues.queue import Queue
from jss.simulate.event import MachineFinishEvent, NewJobEvent, SimulationEvent


class MachineQueueItem:
    job: Job
    op_index: int

    def __init__(self, job: Job, op_index: int):
        self.job = job
        self.op_index = op_index

    def get_operation(self) -> Operation:
        return self.job.operations[self.op_index]

    pass


VERBOSE = getenv("VERBOSE") == "1"


class MachineQueue(Queue[MachineQueueItem]):
    base: Queue[MachineQueueItem]
    machine: int
    total_work: Time
    busy_time: Time

    def __init__(self, base: Queue[MachineQueueItem], machine: int):
        self.base = base
        self.machine = machine
        self.total_work = Time(0)
        self.busy_time = Time(0)

    @override
    def push(self, value: MachineQueueItem):
        self.base.push(value)
        self.total_work += value.get_operation().get_processing_time(self.machine)

    @override
    def pop(self) -> MachineQueueItem | None:
        item = self.base.pop()
        if item is None:
            return None
        processing_time = item.get_operation().get_processing_time(self.machine)
        self.total_work -= processing_time
        self.busy_time += processing_time
        return item

    @override
    def __len__(self) -> int:
        return len(self.base)


class Simulation:
    problem: FJSS
    now: Time
    events: PriorityQueue[SimulationEvent, Time]
    machine_queues: list[MachineQueue]
    machines_busy_until: list[Time]
    routing_rule: Callable[[Self, Job, int], int]

    def __init__(
        self,
        problem: FJSS,
        make_queue: Callable[[Self, int], Queue[MachineQueueItem]],
        routing_rule: Callable[[Self, Job, int], int],
    ):
        """
        Initialize a FJSS simulation with routing rule specified by
        routing_rule and sequencing rule specified by make_queue (via the
        internal queue implementation)

        Args:
            make_queue: A function taking the Simulation object and the machine index,
                        and output a queue that can contain MachineQueueItem elements.
            routing_rule: A function taking the Simulation object, the job and the
                          operation index, and output the machine index to submit this
                          operation to.
        """
        self.problem = problem
        self.now = Time(0)
        self.events = PriorityQueue(
            (NewJobEvent(job) for job in problem.generate_jobs()),
            lambda event: event.arrival_time(),
        )
        self.machine_queues = [
            MachineQueue(make_queue(self, i), i) for i in range(problem.num_machines)
        ]
        self.machines_busy_until = [Time(0) for _ in range(problem.num_machines)]
        self.routing_rule = routing_rule

    def simulate(self) -> Time:
        while True:
            event = self.events.pop()
            if event is None:
                break
            self.now = event.arrival_time()
            self.handle_event(event)
        return self.now

    def handle_event(self, event: SimulationEvent):
        if isinstance(event, NewJobEvent):
            self.handle_new_job(event)
        elif isinstance(event, MachineFinishEvent):
            self.handle_machine_finish(event)
        else:
            raise ValueError("invalid event type")

    def update_queue(self, machine: int):
        if self.now < self.machines_busy_until[machine]:
            return
        item = self.machine_queues[machine].pop()
        if item is None:
            return
        processing_time = item.get_operation().get_processing_time(machine)
        finish_time = self.now + processing_time
        finish_event = MachineFinishEvent(finish_time, machine, item.job, item.op_index)
        self.machines_busy_until[machine] = finish_time
        self.log(
            f"Machine {machine + 1} starts processing operation {item.get_operation().name} at time {self.now}"
        )
        self.events.push(finish_event)

    def handle_new_operation(self, job: Job, op_index: int):
        if op_index >= len(job.operations):
            return
        machine = self.routing_rule(self, job, op_index)
        self.log(
            f"Routing operation {job.operations[op_index].name} to machine {machine + 1} at time {self.now}"
        )
        self.machine_queues[machine].push(MachineQueueItem(job, op_index))
        self.update_queue(machine)

    def handle_new_job(self, event: NewJobEvent):
        self.log(f"Job {event.job.name} started at time {self.now}")
        self.handle_new_operation(event.job, 0)

    def handle_machine_finish(self, event: MachineFinishEvent):
        self.log(
            f"Machine {event.machine + 1} finished operation {event.job.operations[event.operation_index].name} at time {self.now}"
        )
        next_op_index = event.operation_index + 1
        if next_op_index < len(event.job.operations):
            self.handle_new_operation(event.job, next_op_index)
        self.update_queue(event.operation_index)

    def log(self, s: str):
        global VERBOSE
        if VERBOSE:
            print(s)
