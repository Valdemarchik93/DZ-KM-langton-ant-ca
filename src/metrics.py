"""Метрики и классификация режимов."""

import numpy as np


def distance_from_start(ant):
    i, j = ant.ant_position_original()
    di = i - ant.start_i
    dj = j - ant.start_j
    return float(np.hypot(di, dj))


def black_ratio(grid):
    return float(grid.mean())


def visited_area(grid):
    return int((grid != 0).sum())


def _shift_crop(a, b, di, dj):
    """Сравнивает a и b со сдвигом b на (di, dj)."""
    h, w = a.shape
    i0a, i1a = max(0, -di), min(h, h - di)
    j0a, j1a = max(0, -dj), min(w, w - dj)
    if i0a >= i1a or j0a >= j1a:
        return False

    i0b, i1b = i0a + di, i1a + di
    j0b, j1b = j0a + dj, j1a + dj

    sub_a = a[i0a:i1a, j0a:j1a]
    sub_b = b[i0b:i1b, j0b:j1b]
    return np.array_equal(sub_a, sub_b)


def detect_highway(history, periods=(104,), max_snapshots=None,
                   require_full_match=False):
    """Детектор хайвея по истории (список (t, grid))."""
    if len(history) < 2:
        return None

    snapshots = {t: g for t, g in history}
    ts = sorted(snapshots.keys())

    pairs = [(ts[i], ts[i + 1]) for i in range(len(ts) - 1)]
    if max_snapshots is not None:
        pairs = pairs[-max_snapshots:]

    for t_prev, t_cur in pairs:
        for p in periods:
            t_target = t_cur - p
            if t_target not in snapshots:
                continue
            g_prev = snapshots[t_target]
            g_cur = snapshots[t_cur]

            if g_prev.shape != g_cur.shape:
                if require_full_match:
                    continue

            for di in range(-3, 4):
                for dj in range(-3, 4):
                    if di == 0 and dj == 0:
                        continue
                    if _shift_crop(g_cur, g_prev, di, dj):
                        return t_cur, p, di, dj
    return None


def steps_to_highway(history, periods=(104,)):
    res = detect_highway(history, periods=periods)
    if res is None:
        return None
    return res[0]


def classify_regime(area_history, steps):
    """Классифицирует режим движения по истории посещённой площади.

    area_history: список значений площади на разных шагах
    steps: общее число шагов
    """
    if not area_history:
        return "unknown"

    # Смотрим на последние 20% времени
    idx = int(len(area_history) * 0.8)
    late_area = area_history[idx:]

    if len(late_area) < 2:
        return "unknown"

    # Насколько выросла площадь в конце
    growth = late_area[-1] - late_area[0]

    # Если площадь почти не растёт — ограниченное движение
    if growth < 5:
        return "bounded"
    # Если растёт медленно и стабильно — магистраль/хайвей
    elif growth < 100:
        return "highway"
    # Если растёт быстро — неограниченный рост
    else:
        return "unbounded"