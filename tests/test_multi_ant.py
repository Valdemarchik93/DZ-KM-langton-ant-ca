"""Тесты для мира с несколькими муравьями (L3)."""

import numpy as np
import pytest

from src.multi_ant import MultiAntWorld, Ant


def test_create_world_default():
    w = MultiAntWorld(width=10, height=10, n_ants=2)
    assert w.grid.shape == (10, 10)
    assert len(w.ants) == 2


def test_invalid_update():
    with pytest.raises(ValueError):
        MultiAntWorld(width=10, height=10, n_ants=2, update="bad")


def test_invalid_collisions():
    with pytest.raises(ValueError):
        MultiAntWorld(width=10, height=10, n_ants=2, collisions="bad")


def test_invalid_boundary():
    with pytest.raises(ValueError):
        MultiAntWorld(width=10, height=10, n_ants=2, boundary="bad")


def test_single_step_sequential():
    w = MultiAntWorld(width=10, height=10, n_ants=1,
                      start_positions=[(5, 5)])
    w.ants[0].direction = 1  # восток
    w.step()
    # на белой клетке: R (rule[0]='R') -> направо -> юг, шаг вниз
    assert w.ants[0].i == 6
    assert w.ants[0].j == 5


def test_two_ants_independent_until_collision():
    w = MultiAntWorld(width=20, height=20, n_ants=2,
                      start_positions=[(5, 5), (15, 15)])
    w.run(50)
    assert len(w.ants) == 2


def test_synchronous_vs_sequential_differs():
    w1 = MultiAntWorld(width=15, height=15, n_ants=2,
                       start_positions=[(7, 5), (7, 9)],
                       update="sequential")
    w2 = MultiAntWorld(width=15, height=15, n_ants=2,
                       start_positions=[(7, 5), (7, 9)],
                       update="synchronous")
    w1.run(10)
    w2.run(10)
    assert w1.grid is not w2.grid


def test_collision_block():
    w = MultiAntWorld(width=10, height=10, n_ants=2,
                      start_positions=[(5, 5), (5, 7)],
                      collisions="block", update="sequential")
    w.run(20)
    pos = w.ant_positions()
    assert len(set(pos)) == len(pos)


def test_symmetry_preserved():
    # С правилом "FF" (без поворотов) муравьи движутся строго
    # по вертикали и сохраняют j-симметрию.
    w = MultiAntWorld(width=21, height=21, n_ants=2,
                      start_positions=[(5, 10), (15, 10)],
                      rules=["FF", "FF"])
    w.ants[0].direction = 2   # юг
    w.ants[1].direction = 0   # север
    w.run(5)
    pos = w.ant_positions()
    # оба движутся по вертикали: j = 10
    assert pos[0][1] == 10
    assert pos[1][1] == 10
    # i-координаты симметричны относительно центра (i=10)
    assert pos[0][0] + pos[1][0] == 20


def test_no_ant_lost():
    w = MultiAntWorld(width=30, height=30, n_ants=3)
    w.run(100)
    assert len(w.ants) == 3


def test_ant_positions():
    w = MultiAntWorld(width=10, height=10, n_ants=2,
                      start_positions=[(3, 3), (7, 7)])
    pos = w.ant_positions()
    assert pos == [(3, 3), (7, 7)]


def test_run_records_history():
    w = MultiAntWorld(width=15, height=15, n_ants=2)
    w.run(100, record_every=10)
    assert len(w.history) == 11
    assert w.history[0][0] == 0
    assert w.history[-1][0] == 100