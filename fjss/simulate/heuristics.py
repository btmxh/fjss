from typing import Callable
from fjss.problem import Job, Time
from fjss.queues.fifo_queue import FIFOQueue
from fjss.queues.priority_queue import PriorityQueue
from fjss.simulate.simulation import MachineQueueItem, Simulation

FIFOMachineQueue = FIFOQueue[MachineQueueItem]


class SPTMachineQueue(PriorityQueue[MachineQueueItem, Time]):
    def __init__(self, sim: Simulation, machine: int):
        super().__init__(
            [], key_fn=lambda item: item.get_operation().get_processing_time(machine)
        )


RoutingRule = Callable[[Simulation, Job, int], int]


def routing_rule_lwq(sim: Simulation, job: Job, op_index: int) -> int:
    return min(
        job.operations[op_index].get_machines(),
        key=lambda machine: sim.machine_queues[machine].total_work,
    )


def routing_rule_lqs(sim: Simulation, job: Job, op_index: int) -> int:
    return min(
        job.operations[op_index].get_machines(),
        key=lambda machine: len(sim.machine_queues[machine]),
    )


def routing_rule_ert(sim: Simulation, job: Job, op_index: int) -> int:
    return min(
        job.operations[op_index].get_machines(),
        key=lambda machine: sim.machines_busy_until[machine],
    )


def routing_rule_sbt(sim: Simulation, job: Job, op_index: int) -> int:
    return min(
        job.operations[op_index].get_machines(),
        key=lambda machine: sim.machine_queues[machine].busy_time,
    )
