"""Запуск сценариев симуляции."""

import numpy as np
from itertools import product

from src.ant import LangtonAnt
from src.multi_color_ant import MultiColorAnt, VALID_COMMANDS
from src.multi_ant import MultiAntWorld
from src.metrics import (
    black_ratio,
    visited_area,
    steps_to_highway,
    classify_regime,
)


def run_l1_scenario(width=100, height=100, steps=12000,
                    boundary="torus", seed=1097, record_every=50):
    """Запускает один сценарий L1 и собирает статистику."""
    np.random.seed(seed)
    ant = LangtonAnt(width=width, height=height, boundary=boundary)
    ant.run(steps, record_every=record_every)

    history = ant.history if hasattr(ant, "history") else []

    t_list, black_list, area_list = [], [], []
    for t, grid in history:
        t_list.append(t)
        black_list.append(black_ratio(grid))
        area_list.append(visited_area(grid))

    highway_t = steps_to_highway(history, periods=(104,))

    return {
        "ant": ant,
        "history": history,
        "t": t_list,
        "black": black_list,
        "area": area_list,
        "highway_t": highway_t,
    }


def run_l2_scenario(rule, width=150, height=150, steps=5000,
                    boundary="torus", record_every=25):
    """Запускает один сценарий L2."""
    ant = MultiColorAnt(
        rule_string=rule,
        width=width, height=height,
        boundary=boundary,
    )
    ant.run(steps, record_every=record_every)

    history = ant.history if hasattr(ant, "history") else []

    t_list, area_list = [], []
    for t, grid in history:
        t_list.append(t)
        area_list.append(visited_area(grid))

    return {
        "ant": ant,
        "history": history,
        "t": t_list,
        "area": area_list,
        "q": ant.q,
        "shape": ant.grid.shape,
    }


def run_l2_sweep(max_q=4, steps=2000, width=100, height=100):
    """Перебирает все правила длины q от 2 до max_q и классифицирует."""
    results = []
    for q in range(2, max_q + 1):
        for combo in product(VALID_COMMANDS, repeat=q):
            rule = "".join(combo)
            ant = MultiColorAnt(rule, width=width, height=height,
                                boundary="torus")
            area_history = [0]
            for t in range(1, steps + 1):
                ant.step()
                if t % 50 == 0:
                    area = int((ant.grid != 0).sum())
                    area_history.append(area)

            regime = classify_regime(area_history, steps)
            final_area = area_history[-1]

            results.append({
                "rule": rule,
                "q": q,
                "regime": regime,
                "final_area": final_area,
            })
    return results


def run_l3_scenario(n_ants=2, width=100, height=100, steps=5000,
                    update="sequential", collisions="allow",
                    boundary="torus", record_every=25,
                    rules=None, start_positions=None):
    """Запускает один сценарий L3 + собирает метрики взаимодействия."""
    from src.metrics import min_pairwise_distance, mean_pairwise_distance

    world = MultiAntWorld(
        width=width, height=height, n_ants=n_ants,
        update=update, collisions=collisions, boundary=boundary,
        rules=rules, start_positions=start_positions,
    )
    world.run(steps, record_every=record_every)

    history = world.history if hasattr(world, "history") else []

    t_list = []
    area_list = []
    min_dist_list = []
    mean_dist_list = []

    for t, grid, positions in history:
        t_list.append(t)
        area_list.append(visited_area(grid))
        if n_ants >= 2:
            md = min_pairwise_distance(positions)
            ad = mean_pairwise_distance(positions)
            min_dist_list.append(md if md is not None else 0.0)
            mean_dist_list.append(ad if ad is not None else 0.0)

    return {
        "world": world,
        "history": history,
        "t": t_list,
        "area": area_list,
        "n_ants": n_ants,
        "min_dist": min_dist_list,
        "mean_dist": mean_dist_list,
    }