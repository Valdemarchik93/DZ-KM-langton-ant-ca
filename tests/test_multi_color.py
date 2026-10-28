"""Тесты для многоцветного муравья Лэнгтона (L2)."""

import numpy as np
import pytest

from src.multi_color_ant import MultiColorAnt, VALID_COMMANDS


def test_rule_length_equals_colors():
    ant = MultiColorAnt("RLLR", width=5, height=5)
    assert ant.q == 4
    assert ant.rule_string == "RLLR"


def test_invalid_command():
    with pytest.raises(ValueError):
        MultiColorAnt("RLXR", width=5, height=5)


def test_empty_rule():
    with pytest.raises(ValueError):
        MultiColorAnt("", width=5, height=5)


def test_invalid_boundary():
    with pytest.raises(ValueError):
        MultiColorAnt("RL", width=5, height=5, boundary="bad")


def test_color_cycle():
    ant = MultiColorAnt("RLRL", width=5, height=5, start=(2, 2), start_dir=1)
    ant.step()
    assert ant.grid[2, 2] == 1

def test_color_cycle_wraps():
    ant = MultiColorAnt("RL", width=5, height=5, start=(2, 2), start_dir=1)
    ant.grid[2, 2] = 1
    ant.step()
    assert ant.grid[2, 2] == 0


def test_f_command_no_turn():
    ant = MultiColorAnt("F", width=5, height=5, start=(2, 2), start_dir=1)
    ant.step()
    assert ant.ant_position_grid() == (2, 3)
    assert ant.ant_dir == 1


def test_u_turn():
    ant = MultiColorAnt("U", width=5, height=5, start=(2, 2), start_dir=1)
    ant.step()
    assert ant.ant_dir == 3
    assert ant.ant_position_grid() == (2, 1)


def test_l_turn_left():
    ant = MultiColorAnt("L", width=5, height=5, start=(2, 2), start_dir=1)
    ant.step()
    assert ant.ant_dir == 0
    assert ant.ant_position_grid() == (1, 2)


def test_r_turn_right():
    ant = MultiColorAnt("R", width=5, height=5, start=(2, 2), start_dir=1)
    ant.step()
    assert ant.ant_dir == 2
    assert ant.ant_position_grid() == (3, 2)


def test_torus_wrap_l2():
    ant = MultiColorAnt("R", width=5, height=5, start=(0, 0),
                        start_dir=1, boundary="torus")
    ant.step()
    assert ant.ant_position_grid() == (1, 0)


def test_valid_commands_constant():
    assert set(VALID_COMMANDS) == {"R", "L", "F", "U"}


def test_run_records_history():
    ant = MultiColorAnt("RLR", width=10, height=10)
    ant.run(100, record_every=10)
    assert len(ant.history) == 11
    assert ant.history[0][0] == 0
    assert ant.history[-1][0] == 100