"""Мир из нескольких муравьёв Лэнгтона (L3)."""

import numpy as np

DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class Ant:
    """Один муравей: позиция, направление, правило."""

    def __init__(self, i, j, direction=0, rule=None):
        self.i = i
        self.j = j
        self.direction = direction
        self.rule = rule if rule is not None else "RL"

    def __repr__(self):
        return f"Ant({self.i}, {self.j}, dir={self.direction})"


class MultiAntWorld:
    """Мир, в котором живут несколько муравьёв.

    Параметры:
    - width, height: размеры поля
    - n_ants: число муравьёв
    - update: "sequential" или "synchronous"
    - collisions: "allow" (несколько в клетке) или "block" (нельзя)
    - boundary: "torus" или "expand"
    """

    def __init__(self, width=100, height=100, n_ants=2,
                 update="sequential", collisions="allow",
                 boundary="torus", start_positions=None,
                 rules=None):
        if update not in ("sequential", "synchronous"):
            raise ValueError("update must be 'sequential' or 'synchronous'")
        if collisions not in ("allow", "block"):
            raise ValueError("collisions must be 'allow' or 'block'")
        if boundary not in ("torus", "expand"):
            raise ValueError("boundary must be 'torus' or 'expand'")

        self.width = width
        self.height = height
        self.update = update
        self.collisions = collisions
        self.boundary = boundary

        self.grid = np.zeros((height, width), dtype=np.uint8)

        if start_positions is None:
            start_positions = []
            cx, cy = height // 2, width // 2
            radius = min(height, width) // 4
            for k in range(n_ants):
                angle = 2 * np.pi * k / n_ants
                i = int(cx + radius * np.sin(angle))
                j = int(cy + radius * np.cos(angle))
                i = max(0, min(height - 1, i))
                j = max(0, min(width - 1, j))
                start_positions.append((i, j))

        if rules is None:
            rules = ["RL"] * n_ants

        self.ants = [
            Ant(i, j, direction=0, rule=rules[k])
            for k, (i, j) in enumerate(start_positions[:n_ants])
        ]

        self.step_count = 0

    def _wrap(self, i, j):
        return i % self.height, j % self.width

    def _in_bounds(self, i, j):
        return 0 <= i < self.height and 0 <= j < self.width

    def _step_ant(self, ant):
        """Делает один шаг для муравья. Возвращает (старая, новая) позиции."""
        color = int(self.grid[ant.i, ant.j])
        cmd = ant.rule[color] if color < len(ant.rule) else "R"

        if cmd == "R":
            ant.direction = (ant.direction + 1) % 4
        elif cmd == "L":
            ant.direction = (ant.direction - 1) % 4
        elif cmd == "U":
            ant.direction = (ant.direction + 2) % 4

        q = len(ant.rule)
        self.grid[ant.i, ant.j] = (color + 1) % q

        di, dj = DIRECTIONS[ant.direction]
        ni, nj = ant.i + di, ant.j + dj

        if self.boundary == "torus":
            ni, nj = self._wrap(ni, nj)
        else:
            if not self._in_bounds(ni, nj):
                return (ant.i, ant.j), (ant.i, ant.j)

        if self.collisions == "block":
            for other in self.ants:
                if other is ant:
                    continue
                if (other.i, other.j) == (ni, nj):
                    return (ant.i, ant.j), (ant.i, ant.j)

        old = (ant.i, ant.j)
        ant.i, ant.j = ni, nj
        return old, (ni, nj)

    def step(self):
        """Один шаг мира."""
        if self.update == "sequential":
            for ant in self.ants:
                self._step_ant(ant)
        else:  # synchronous
            moves = []
            for ant in self.ants:
                old_i, old_j = ant.i, ant.j
                _, new_pos = self._step_ant(ant)
                moves.append(new_pos)
                ant.i, ant.j = old_i, old_j

            for k, ant in enumerate(self.ants):
                ni, nj = moves[k]
                ant.i, ant.j = ni, nj

        self.step_count += 1

    def run(self, n_steps, record_every=0):
        if record_every > 0:
            self.history = [(0, self.grid.copy(),
                             [(a.i, a.j) for a in self.ants])]
            for k in range(1, n_steps + 1):
                self.step()
                if k % record_every == 0:
                    self.history.append(
                        (k, self.grid.copy(), [(a.i, a.j) for a in self.ants])
                    )
        else:
            for _ in range(n_steps):
                self.step()
        return self

    def ant_positions(self):
        return [(a.i, a.j) for a in self.ants]