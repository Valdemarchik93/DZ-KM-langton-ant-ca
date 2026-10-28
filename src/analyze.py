"""Анализ результатов sweep и генерация отчёта."""

import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, defaultdict

from src.simulate import run_l2_scenario
from src.visualize import create_multicolor_gif, save_frame


def load_sweep(path="results/sweep/sweep_results.json"):
    """Загружает результаты sweep."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def plot_regime_distribution(results, path="results/sweep/regime_distribution.png"):
    """Столбчатая диаграмма распределения режимов (общая)."""
    regimes = Counter(r["regime"] for r in results)
    labels = list(regimes.keys())
    values = list(regimes.values())

    colors = {
        "bounded": "#377EB8",
        "highway": "#4DAF4A",
        "unbounded": "#E41A1C",
        "unknown": "#999999",
    }
    bar_colors = [colors.get(l, "#999999") for l in labels]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=bar_colors)
    ax.set_xlabel("Режим")
    ax.set_ylabel("Число правил")
    ax.set_title("Распределение режимов по всем правилам (q=2..4)")
    ax.grid(True, alpha=0.3, axis="y")

    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1,
                str(v), ha="center", va="bottom", fontsize=11)

    plt.tight_layout()
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[analyze] Сохранено: {path}")
    return regimes


def plot_regime_by_q(results, path="results/sweep/regime_by_q.png"):
    """Сгруппированная диаграмма: по q — доли режимов."""
    by_q = defaultdict(Counter)
    for r in results:
        by_q[r["q"]][r["regime"]] += 1

    qs = sorted(by_q.keys())
    regimes = ["bounded", "highway", "unbounded"]
    colors = {
        "bounded": "#377EB8",
        "highway": "#4DAF4A",
        "unbounded": "#E41A1C",
    }

    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.25
    x = np.arange(len(qs))

    for i, reg in enumerate(regimes):
        counts = [by_q[q].get(reg, 0) for q in qs]
        ax.bar(x + (i - 1) * width, counts, width, label=reg,
               color=colors[reg])

    ax.set_xlabel("Число цветов q")
    ax.set_ylabel("Число правил")
    ax.set_title("Распределение режимов по числу цветов q")
    ax.set_xticks(x)
    ax.set_xticklabels([f"q={q}" for q in qs])
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[analyze] Сохранено: {path}")


def find_top_rules(results, regime, n=3, steps=3000):
    """Возвращает топ-N правил для данного режима по финальной площади."""
    candidates = [r for r in results if r["regime"] == regime]
    candidates.sort(key=lambda r: r["final_area"], reverse=True)
    return candidates[:n]


def generate_top_gifs(results, out_dir="results/sweep/top", steps=3000):
    """Генерирует GIF и кадры для топ-правил каждого режима."""
    os.makedirs(out_dir, exist_ok=True)

    for regime in ["bounded", "highway", "unbounded"]:
        top = find_top_rules(results, regime, n=3)
        for i, r in enumerate(top):
            rule = r["rule"]
            print(f"[analyze] {regime} top-{i+1}: {rule} "
                  f"(area={r['final_area']})")

            out = os.path.join(out_dir, f"{regime}_{i+1}_{rule}")
            os.makedirs(out, exist_ok=True)

            res = run_l2_scenario(
                rule=rule, width=150, height=150, steps=steps,
                boundary="torus", record_every=max(1, steps // 100),
            )

            create_multicolor_gif(
                res["history"],
                path=os.path.join(out, "animation.gif"),
                q=res["q"],
                frame_step=max(1, steps // 100),
                fps=10,
            )
            save_frame(
                res["history"], t_target=steps,
                path=os.path.join(out, "final_frame.png"),
                q=res["q"],
            )


def print_summary(results):
    """Печатает сводку по режимам."""
    by_q = defaultdict(Counter)
    for r in results:
        by_q[r["q"]][r["regime"]] += 1

    print("\n=== Разбивка по q ===")
    for q in sorted(by_q.keys()):
        total = sum(by_q[q].values())
        print(f"\nq={q} (всего {total} правил):")
        for reg in ["bounded", "highway", "unbounded"]:
            cnt = by_q[q].get(reg, 0)
            pct = 100 * cnt / total if total else 0
            print(f"  {reg:10s}: {cnt:3d} ({pct:5.1f}%)")


def main():
    results = load_sweep()
    print(f"Загружено {len(results)} правил")

    plot_regime_distribution(results)
    plot_regime_by_q(results)
    print_summary(results)

    print("\nГенерация GIF для топ-3 каждого режима...")
    generate_top_gifs(results)


if __name__ == "__main__":
    main()