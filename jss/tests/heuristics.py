from jss.problem import StaticFJSS, StaticFJSSSet
from jss.simulate.simulation import Simulation
from jss.simulate.heuristics import (
    FIFOMachineQueue,
    SPTMachineQueue,
    routing_rule_lwq,
)
from sys import argv


def make_sim(problem: StaticFJSS) -> Simulation:
    return Simulation(
        problem,
        make_queue=lambda self, machine: SPTMachineQueue(self, machine),
        routing_rule=routing_rule_lwq,
    )


if __name__ == "__main__":
    problemset = StaticFJSSSet(argv[1])
    total_normalized_makespan = 0
    for problem in problemset.problems:
        total_time = make_sim(problem).simulate()
        normalized_makespan = total_time / (problem.lower_bound or float("nan"))
        print(problem.name, problem.lower_bound, total_time, normalized_makespan)
        total_normalized_makespan += normalized_makespan
    total_normalized_makespan /= len(problemset.problems)
    print(total_normalized_makespan)
