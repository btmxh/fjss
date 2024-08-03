from sys import argv
from jss.gp.ccgp import CCGP
from jss.problem import StaticFJSSSet


problemset = StaticFJSSSet(argv[1])
ccgp = CCGP()

for i, (routing_rule, sequencing_rule) in zip(
    range(1, 52), ccgp.run_static(problemset)
):
    print(i, ccgp.normalized_makespan(routing_rule, sequencing_rule, problemset))
    print(routing_rule)
    print(sequencing_rule)
