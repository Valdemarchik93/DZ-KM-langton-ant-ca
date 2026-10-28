"""Командный интерфейс для запуска симуляций."""

import os
import json
import click
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.simulate import run_l1_scenario, run_l2_scenario, run_l2_sweep
from src.visualize import (
    plot_black_ratio,
    plot_visited_area,
    create_gif,
    save_frame,
    create_multicolor_gif,
)


@click.group()
def cli():
    """CLI для модели муравья Лэнгтона."""
    pass


@cli.command()
@click.option("--width", default=100, help="Ширина поля")
@click.option("--height", default=100, help="Высота поля")
@click.option("--steps", default=12000, help="Число шагов")
@click.option("--boundary", default="torus",
              type=click.Choice(["torus", "expand"]),
              help="Граничные условия")
@click.option("--record-every", default=50,
              help="Сохранять снимок каждые N шагов")
@click.option("--output", default="results/l1", help="Папка для результатов")
@click.option("--seed", default=1097, help="Seed")
def run_l1(width, height, steps, boundary, record_every, output, seed):
    """Запускает L1 (классический муравей)."""
    click.echo(f"L1: {width}x{height}, {steps} шагов, boundary={boundary}")
    os.makedirs(output, exist_ok=True)

    result = run_l1_scenario(
        width=width, height=height, steps=steps,
        boundary=boundary, seed=seed, record_every=record_every,
    )

    plot_black_ratio(result, path=os.path.join(output, "black_ratio.png"))
    plot_visited_area(result, path=os.path.join(output, "visited_area.png"))
    plt.close("all")

    create_gif(result["history"],
               path=os.path.join(output, "ant_animation.gif"),
               frame_step=record_every, fps=10)
    save_frame(result["history"], t_target=min(10000, steps),
               path=os.path.join(output, "frame_10000.png"))

    click.echo("\n=== Сводка ===")
    click.echo(f"  шагов: {steps}")
    click.echo(f"  финальная площадь: {result['area'][-1]}")
    click.echo(f"  финальная доля чёрных: {result['black'][-1]:.4f}")
    if result["highway_t"] is not None:
        click.echo(f"  хайвей обнаружен на шаге: {result['highway_t']}")
    else:
        click.echo("  хайвей не обнаружен")


@cli.command()
@click.option("--rule", required=True, help="Строка правил, например RLLR")
@click.option("--width", default=150, help="Ширина поля")
@click.option("--height", default=150, help="Высота поля")
@click.option("--steps", default=5000, help="Число шагов")
@click.option("--boundary", default="torus",
              type=click.Choice(["torus", "expand"]),
              help="Граничные условия")
@click.option("--record-every", default=25,
              help="Сохранять снимок каждые N шагов")
@click.option("--output", default=None, help="Папка результатов")
def run_l2(rule, width, height, steps, boundary, record_every, output):
    """Запускает L2 (многоцветный муравей)."""
    if output is None:
        output = os.path.join("results", f"l2_{rule}")

    click.echo(f"L2: rule={rule}, {width}x{height}, {steps} шагов")
    os.makedirs(output, exist_ok=True)

    result = run_l2_scenario(
        rule=rule, width=width, height=height, steps=steps,
        boundary=boundary, record_every=record_every,
    )

    plt.close("all")

    create_multicolor_gif(
        result["history"],
        path=os.path.join(output, "animation.gif"),
        q=result["q"],
        frame_step=record_every,
        fps=10,
    )
    save_frame(result["history"], t_target=steps,
               path=os.path.join(output, "final_frame.png"),
               q=result["q"])

    click.echo("\n=== Сводка ===")
    click.echo(f"  правило: {rule}")
    click.echo(f"  шагов: {steps}")
    click.echo(f"  финальная площадь: {result['area'][-1]}")
    click.echo(f"  размер поля: {result['shape']}")


@cli.command()
@click.option("--max-q", default=4, help="Максимальное число цветов")
@click.option("--steps", default=2000, help="Шагов на каждое правило")
@click.option("--output", default="results/sweep", help="Папка для результатов")
def sweep_l2(max_q, steps, output):
    """Перебирает все правила длины q и классифицирует их."""
    click.echo(f"Перебор правил q=2..{max_q}, шагов={steps}")
    os.makedirs(output, exist_ok=True)

    results = run_l2_sweep(max_q=max_q, steps=steps)

    # Группируем по режимам
    by_regime = {}
    for r in results:
        reg = r["regime"]
        if reg not in by_regime:
            by_regime[reg] = []
        by_regime[reg].append(r)

    # Сохраняем в JSON
    with open(os.path.join(output, "sweep_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Сводка
    click.echo("\n=== Результаты классификации ===")
    for reg, items in sorted(by_regime.items()):
        click.echo(f"  {reg}: {len(items)} правил")

    click.echo(f"\nСохранено: {output}/sweep_results.json")
    click.echo(f"Всего проверено: {len(results)} правил")


@cli.command()
def info():
    """Печатает краткую информацию о модели."""
    click.echo("Муравей Лэнгтона - клеточный автомат.")
    click.echo("L1: белая -> налево; чёрная -> направо.")
    click.echo("L2: строка команд R/L/F/U по цветам.")


if __name__ == "__main__":
    cli()