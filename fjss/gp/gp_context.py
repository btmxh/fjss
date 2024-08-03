from collections.abc import Generator
from fjss.gp.program import Node, Program, random_generic, random_internal, random_terminal
from random import choice, random


class GPContext:
    pop_size: int
    max_depth: int

    def __init__(self, pop_size: int = 512, max_depth: int = 8):
        self.pop_size = pop_size
        self.max_depth = max_depth

    def gen_full(self, depth: int) -> Node:
        return (
            random_terminal()
            if depth == 0
            else random_internal(lambda: self.gen_full(depth - 1))
        )

    def gen_grow(self, depth: int) -> Node:
        return (
            random_terminal()
            if depth == 0
            else random_generic(lambda: self.gen_grow(depth - 1))
        )

    def ramp_half_and_half(self) -> Generator[Node, None, None]:
        half_size = self.pop_size // 2
        for depth in range(1, self.max_depth - 1):
            for _ in range(0, half_size // self.max_depth):
                yield self.gen_full(depth)
                yield self.gen_grow(depth)

    def init_population(self) -> list[Program]:
        return [Program(node) for node in self.ramp_half_and_half()]

    def crossover(self, p1: Program, p2: Program) -> Program:
        if random() < 0.5:
            p1, p2 = p2, p1

        p1 = p1.copy()
        p2 = p2.copy()

        h1 = p1.root.height()
        h2 = p2.root.height()
        n1 = choice(p1.root.descendants())

        height_n1 = n1.height()
        depth_n1 = h1 - height_n1

        def suitable_for_n1(n2: Node) -> bool:
            height_n2 = n2.height()
            depth_n2 = h2 - height_n2
            return max(height_n1 + depth_n2, height_n2 + depth_n1) <= self.max_depth

        n2s = [n2 for n2 in p2.root.descendants() if suitable_for_n1(n2)]
        n2 = choice(n2s)

        n1.assign(n2)

        assert p1.root.height() <= self.max_depth
        return p1

    def mutate(self, p: Program) -> Program:
        p = p.copy()
        n = choice(p.root.descendants())
        n.assign(self.gen_grow(self.max_depth - p.root.height() + n.height()))
        assert p.root.height() <= self.max_depth
        return p
