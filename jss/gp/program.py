from collections.abc import Callable
from random import choice, random
from typing import override
from jss.problem import Job
from jss.simulate.simulation import Simulation


class Node:
    node_type: str
    children: list["Node"]

    def __init__(self, node_type: str, children: list["Node"]):
        self.node_type = node_type
        self.children = children

    def swap_with(self, other: "Node"):
        self.node_type, other.node_type = other.node_type, self.node_type
        self.children, other.children = other.children, self.children

    def assign(self, node: "Node"):
        self.node_type = node.node_type
        self.children = node.children

    def calc(self, sim: Simulation, job: Job, op_index: int, machine: int) -> float:
        match self.node_type:
            # terminals
            case "NPT":
                return (
                    float(job.median_work_time[op_index + 1])
                    if op_index + 1 < len(job.operations)
                    else 0.0
                )
            case "WKR":
                return float(job.median_work_remaining[op_index])
            case "NOR":
                return float(len(job.operations) - 1 - op_index)
            case "W":
                return float(1.0)
            case "TIS":
                return float(sim.now)
            case "NIQ":
                return float(len(sim.machine_queues[machine]))
            case "MWT":
                return max(0.0, sim.now - sim.machines_busy_until[machine])
            case "PT":
                return job.operations[op_index].get_processing_time(machine)
            case "OWT":
                return sim.now - job.last_operation_ready_time
            # internal nodes
            case "ADD":
                first = self.children[0].calc(sim, job, op_index, machine)
                secnd = self.children[1].calc(sim, job, op_index, machine)
                return first + secnd
            case "SUB":
                first = self.children[0].calc(sim, job, op_index, machine)
                secnd = self.children[1].calc(sim, job, op_index, machine)
                return first - secnd
            case "MUL":
                first = self.children[0].calc(sim, job, op_index, machine)
                secnd = self.children[1].calc(sim, job, op_index, machine)
                return first * secnd
            case "DIV":
                first = self.children[0].calc(sim, job, op_index, machine)
                secnd = self.children[1].calc(sim, job, op_index, machine)
                return first / secnd if abs(secnd) >= 1e-8 else 1.0
            case "MIN":
                first = self.children[0].calc(sim, job, op_index, machine)
                secnd = self.children[1].calc(sim, job, op_index, machine)
                return min(first, secnd)
            case "MAX":
                first = self.children[0].calc(sim, job, op_index, machine)
                secnd = self.children[1].calc(sim, job, op_index, machine)
                return max(first, secnd)
            case _:
                raise ValueError("invalid GP node")

    def copy(self) -> "Node":
        return Node(self.node_type, [child.copy() for child in self.children])

    def height(self) -> int:
        return max((child.height() + 1 for child in self.children), default=0)

    def descendants(self) -> list["Node"]:
        return [self] + [
            desc for child in self.children for desc in child.descendants()
        ]

    @override
    def __str__(self) -> str:
        return self.node_type + (
            ""
            if len(self.children) == 0
            else ("(" + ",".join(str(child) for child in self.children) + ")")
        )


def random_terminal():
    return Node(
        choice(["NPT", "WKR", "NOR", "W", "TIS", "NIQ", "MWT", "PT", "OWT"]), []
    )


def random_internal(child_gen: Callable[[], Node]):
    return Node(
        choice(["ADD", "SUB", "MUL", "DIV", "MIN", "MAX"]),
        [child_gen() for _ in range(2)],
    )


def random_generic(child_gen: Callable[[], Node]):
    return random_terminal() if random() < 9 / 15 else random_internal(child_gen)


class Program:
    root: Node
    fitness: float
    last_evaluated_with: "Program | None"

    def __init__(self, root: Node) -> None:
        self.root = root
        self.fitness = float("inf")
        self.last_evaluated_with = None

    def copy(self) -> "Program":
        return Program(self.root.copy())

    @override
    def __str__(self) -> str:
        return f"{self.root} (fitness {self.fitness})"
