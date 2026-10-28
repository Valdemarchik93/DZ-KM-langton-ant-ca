"""Классический муравей Лэнгтона (L1)."""

import numpy as np

# Направления: 0 = север (вверх, -1 по i), 1 = восток (+1 по j),
#              2 = юг (+1 по i), 3 = запад (-1 по j)
DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class LangtonAnt:
    """Классический муравей Лэнгтона: 2 цвета, 1 муравей.

    Правило:
    - на белой клетке (0): поворот налево, перекрасить в 1;
    - на чёрной клетке (1): поворот направо, перекрасить в 0;
    - затем шаг вперёд.
    """

    def __init__(self, width=100, height=100, boundary="torus",
                 start=None, start_dir=1):
        if boundary not in ("torus", "expand"):
            raise ValueError("boundary must be 'torus' or 'expand'")

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
        """Для boundary='expand': расширяет поле, если муравей вышел.
        Возвращает новые (i, j) в системе координат расширенного поля.
        """
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
        """Для boundary='torus': заворот координат по модулю."""
        h, w = self.grid.shape
        return i % h, j % w

    def step(self):
        """Один шаг муравья."""
        color = int(self.grid[self.ant_i, self.ant_j])

        if color == 0:
            self.ant_dir = (self.ant_dir - 1) % 4
            self.grid[self.ant_i, self.ant_j] = 1
        else:
            self.ant_dir = (self.ant_dir + 1) % 4
            self.grid[self.ant_i, self.ant_j] = 0

        di, dj = DIRECTIONS[self.ant_dir]
        ni, nj = self.ant_i + di, self.ant_j + dj

        if self.boundary == "torus":
            ni, nj = self._wrap(ni, nj)
        else:
            ni, nj = self._ensure_inside(ni, nj)

        self.ant_i, self.ant_j = ni, nj
        self.step_count += 1

    def run(self, n_steps, record_every=0):
        """Запускает n_steps шагов."""
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