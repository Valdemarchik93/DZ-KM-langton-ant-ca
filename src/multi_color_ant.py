"""Многоцветный муравей Лэнгтона (L2)."""

import numpy as np

# Направления: 0 = север, 1 = восток, 2 = юг, 3 = запад
DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

# Допустимые команды в строке правил
VALID_COMMANDS = ("R", "L", "F", "U")


class MultiColorAnt:
    """Многоцветный муравей Лэнгтона.

    Правило: строка rule_string длины q, где q — число цветов.
    Каждый символ задаёт команду для соответствующего цвета:
    - 'R' — поворот направо;
    - 'L' — поворот налево;
    - 'F' — движение без поворота;
    - 'U' — разворот на 180°.

    После поворота цвет клетки циклически меняется: (s + 1) mod q.
    Затем муравей делает шаг вперёд.
    """

    def __init__(self, rule_string, width=100, height=100, boundary="torus",
                 start=None, start_dir=0):
        if not rule_string:
            raise ValueError("rule_string must be non-empty")
        for ch in rule_string:
            if ch not in VALID_COMMANDS:
                raise ValueError(
                    f"invalid command '{ch}', "
                    f"expected one of {VALID_COMMANDS}"
                )

        if boundary not in ("torus", "expand"):
            raise ValueError("boundary must be 'torus' or 'expand'")

        self.rule_string = rule_string
        self.q = len(rule_string)
        self.boundary = boundary

        self.grid = np.zeros((height, width), dtype=np.uint8)

        if start is None:
            start = (height // 2, width // 2)
        self.ant_i, self.ant_j = start
        self.ant_dir = start_dir

        self.start_i, self.start_j = start
        self.offset_i = 0
        self.offset_j = 0

        self.step_count = 0

    def _ensure_inside(self, i, j):
        """Расширяет поле, если муравей вышел. Возвращает (i, j)."""
        h, w = self.grid.shape
        pad_top = max(0, -i)
        pad_bottom = max(0, i - (h - 1))
        pad_left = max(0, -j)
        pad_right = max(0, j - (w - 1))
        if pad_top or pad_bottom or pad_left or pad_right:
            self.grid = np.pad(
                self.grid,
                ((pad_top, pad_bottom), (pad_left, pad_right)),
                mode="constant",
                constant_values=0,
            )
            self.offset_i -= pad_top
            self.offset_j -= pad_left
            i += pad_top
            j += pad_left
        return i, j

    def _wrap(self, i, j):
        h, w = self.grid.shape
        return i % h, j % w

    def _apply_command(self, cmd):
        """Меняет направление муравья согласно команде."""
        if cmd == "R":
            self.ant_dir = (self.ant_dir + 1) % 4
        elif cmd == "L":
            self.ant_dir = (self.ant_dir - 1) % 4
        elif cmd == "F":
            pass
        elif cmd == "U":
            self.ant_dir = (self.ant_dir + 2) % 4

    def step(self):
        """Один шаг многоцветного муравья."""
        color = int(self.grid[self.ant_i, self.ant_j])
        cmd = self.rule_string[color]

        # 1) поворот
        self._apply_command(cmd)

        # 2) смена цвета по циклу
        self.grid[self.ant_i, self.ant_j] = (color + 1) % self.q

        # 3) шаг вперёд
        di, dj = DIRECTIONS[self.ant_dir]
        ni, nj = self.ant_i + di, self.ant_j + dj

        if self.boundary == "torus":
            ni, nj = self._wrap(ni, nj)
        else:
            ni, nj = self._ensure_inside(ni, nj)

        self.ant_i, self.ant_j = ni, nj
        self.step_count += 1

    def run(self, n_steps, record_every=0):
        if record_every > 0:
            self.history = [(0, self.grid.copy())]
            for k in range(1, n_steps + 1):
                self.step()
                if k % record_every == 0:
                    self.history.append((k, self.grid.copy()))
        else:
            for _ in range(n_steps):
                self.step()
        return self

    def ant_position_original(self):
        return (self.ant_i + self.offset_i, self.ant_j + self.offset_j)

    def ant_position_grid(self):
        return (self.ant_i, self.ant_j)