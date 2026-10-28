"""Тесты для классического муравья Лэнгтона."""

import numpy as np
import pytest

from src.ant import LangtonAnt
from src.metrics import (
    black_ratio,
    visited_area,
    _shift_crop,
    detect_highway,
)


def test_create_empty_grid():
    ant = LangtonAnt(width=10, height=20)
    assert ant.grid.shape == (20, 10)
    assert ant.grid.dtype == np.uint8
    assert np.all(ant.grid == 0)


def test_start_center_default():
    ant = LangtonAnt(width=10, height=10)
    assert ant.ant_position_grid() == (5, 5)


def test_invalid_boundary():
    with pytest.raises(ValueError):
        LangtonAnt(width=10, height=10, boundary="bad")


def test_first_step_left_turn_on_white():
    ant = LangtonAnt(width=5, height=5, start=(2, 2), start_dir=1)
    ant.step()
    assert ant.grid[2, 2] == 1
    assert ant.ant_position_grid() == (1, 2)
    assert ant.ant_dir == 0


def test_first_step_right_turn_on_black():
    ant = LangtonAnt(width=5, height=5, start=(2, 2), start_dir=1)
    ant.grid[2, 2] = 1
    ant.step()
    assert ant.grid[2, 2] == 0
    assert ant.ant_position_grid() == (3, 2)
    assert ant.ant_dir == 2


def test_torus_wrap():
    ant = LangtonAnt(width=5, height=5, start=(0, 0), start_dir=0,
                     boundary="torus")
    ant.step()
    assert ant.ant_position_grid() == (0, 4)


def test_expand_field_grows():
    ant = LangtonAnt(width=3, height=3, start=(0, 0), start_dir=1,
                     boundary="expand")
    ant.step()
    # start_dir=1 (восток), на белой клетке поворот налево -> север,
    # шаг на север выходит за верхнюю границу -> поле растёт сверху.
    assert ant.grid.shape[0] >= 4
    assert ant.grid.shape[1] >= 3
    # после шага муравей в исходной системе координат ушёл в -1 по i
    assert ant.ant_position_original() == (-1, 0)


def test_expand_field_grows_left():
    ant = LangtonAnt(width=3, height=3, start=(0, 0), start_dir=0,
                     boundary="expand")
    ant.step()
    # start_dir=0 (север), поворот налево -> запад, шаг влево
    # выходит за левую границу -> поле растёт слева.
    assert ant.grid.shape[1] >= 4
    assert ant.grid.shape[0] >= 3
    # после шага муравей в исходной системе координат ушёл в -1 по j
    assert ant.ant_position_original() == (0, -1)


def test_metrics_black_ratio():
    ant = LangtonAnt(width=4, height=4)
    ant.grid[:] = 0
    ant.grid[0, 0] = 1
    assert black_ratio(ant.grid) == 1 / 16


def test_metrics_visited_area():
    ant = LangtonAnt(width=4, height=4)
    ant.grid[:] = 0
    ant.grid[0, 0] = 1
    ant.grid[1, 1] = 1
    assert visited_area(ant.grid) == 2


def test_shift_crop_same():
    a = np.array([[1, 0], [0, 1]], dtype=np.uint8)
    b = np.array([[0, 1], [1, 0]], dtype=np.uint8)
    assert _shift_crop(a, b, 0, 1) is True


def test_shift_crop_different():
    a = np.array([[1, 0], [0, 1]], dtype=np.uint8)
    b = np.array([[1, 1], [1, 1]], dtype=np.uint8)
    assert _shift_crop(a, b, 0, 0) is False


def test_detect_highway_synthetic():
    g = np.zeros((5, 5), dtype=np.uint8)
    history = [(0, g.copy()), (1, g.copy()), (2, g.copy()), (3, g.copy())]
    res = detect_highway(history, periods=(2,))
    assert res is not None
    assert res[1] == 2


def test_detect_highway_no_match():
    g0 = np.zeros((5, 5), dtype=np.uint8)
    g1 = np.ones((5, 5), dtype=np.uint8)
    history = [(0, g0), (1, g1)]
    res = detect_highway(history, periods=(1,))
    assert res is None