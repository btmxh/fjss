from collections.abc import Callable, Generator, Iterable
from statistics import mean
from fjss.gp.gp_context import GPContext
from fjss.gp.program import Program
from fjss.problem import FJSS, StaticFJSS, Time
from fjss.queues.dynamic_priority_queue import DynamicPriorityQueue
from fjss.simulate.simulation import MachineQueueItem, Simulation
from random import choice, choices
from heapq import nsmallest
from multiprocessing import Pool


class CCGP(GPContext):
    def __init__(self):
        super().__init__()

    def run_static(
        self, problems: Iterable[StaticFJSS]
    ) -> Generator[tuple[Program, Program], None, None]:
        yield from self.run(lambda r, s: self.normalized_makespan(r, s, problems))

    def run(
        self, fitness_fn: Callable[[Program, Program], float]
    ) -> Generator[tuple[Program, Program], None, None]:
        routing_pop = self.init_population()
        sequencing_pop = self.init_population()

        ctx_routing = choice(routing_pop)
        ctx_sequencing = choice(routing_pop)

        while True:
            new_routing_pop = self.elitism(routing_pop)
            new_sequencing_pop = self.elitism(sequencing_pop)

            while len(new_routing_pop) < len(routing_pop):
                new_routing_pop.append(self.generate_offspring(routing_pop))
            while len(new_sequencing_pop) < len(sequencing_pop):
                new_sequencing_pop.append(self.generate_offspring(sequencing_pop))

            for routing_rule in new_routing_pop:
                routing_rule.fitness = fitness_fn(routing_rule, ctx_sequencing)
            for sequencing_rule in new_sequencing_pop:
                sequencing_rule.fitness = fitness_fn(ctx_routing, sequencing_rule)
            ctx_routing = min(new_routing_pop + [ctx_routing], key=lambda p: p.fitness)
            ctx_sequencing = min(
                new_sequencing_pop + [ctx_sequencing], key=lambda p: p.fitness
            )
            yield ctx_routing, ctx_sequencing

    def generate_offspring(self, pop: list[Program]) -> Program:
        match choices([1, 2, 3], weights=[80, 15, 5], k=1)[0]:
            case 1:
                p1 = min(choices(pop, k=7), key=lambda p: p.fitness)
                p2 = min(choices(pop, k=7), key=lambda p: p.fitness)
                return self.crossover(p1, p2)
            case 2:
                p = min(choices(pop, k=7), key=lambda p: p.fitness)
                return self.mutate(p)
            case _:
                p = min(choices(pop, k=7), key=lambda p: p.fitness)
                return p.copy()

    def makespan(
        self, routing_rule: Program, sequencing_rule: Program, problem: FJSS
    ) -> Time:
        return Simulation(
            problem,
            make_queue=lambda sim, machine: DynamicPriorityQueue[
                MachineQueueItem, Time
            ](
                key_fn=lambda item: sequencing_rule.root.calc(
                    sim, item.job, item.op_index, machine
                )
            ),
            routing_rule=lambda sim, job, op_index: min(
                job.operations[op_index].get_machines(),
                key=lambda machine: routing_rule.root.calc(sim, job, op_index, machine),
            ),
        ).simulate()

    def normalized_makespan(
        self,
        routing_rule: Program,
        sequencing_rule: Program,
        problems: Iterable[StaticFJSS],
        parallel: int = 12,
    ) -> float:
        return mean(
            Pool(parallel).map(
                normalized_makespan_mp,
                (
                    (self, routing_rule, sequencing_rule, problem)
                    for problem in problems
                ),
            )
        )

    def elitism(self, pop: list[Program], k: int = 2) -> list[Program]:
        return nsmallest(k, pop, key=lambda p: p.fitness)


def makespan_mp(args: tuple[CCGP, Program, Program, FJSS]) -> Time:
    ccgp, routing_rule, sequencing_rule, problem = args
    return ccgp.makespan(routing_rule, sequencing_rule, problem)


def normalized_makespan_mp(args: tuple[CCGP, Program, Program, StaticFJSS]) -> float:
    ccgp, routing_rule, sequencing_rule, problem = args
    return ccgp.makespan(routing_rule, sequencing_rule, problem) / (
        problem.lower_bound or float("nan")
    )
