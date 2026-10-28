"""Визуализация результатов."""

import io
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

CMAP_2 = ListedColormap(["white", "black"])

MULTI_COLORS = [
    "#FFFFFF", "#000000", "#E41A1C", "#377EB8",
    "#4DAF4A", "#984EA3", "#FF7F00", "#FFFF33",
]

ANT_COLORS = ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3",
              "#FF7F00", "#FFFF33"]


def _cmap_for_q(q):
    return ListedColormap(MULTI_COLORS[:q])


def plot_black_ratio(result, path=None):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(result["t"], result["black"], linewidth=2)
    ax.set_xlabel("Время (шаги)")
    ax.set_ylabel("Доля чёрных клеток")
    ax.set_title("Доля чёрных клеток от времени")
    ax.grid(True, alpha=0.3)
    if path:
        fig.savefig(path, dpi=100, bbox_inches="tight")
        plt.close(fig)
    return fig


def plot_visited_area(result, path=None):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(result["t"], result["area"], linewidth=2, color="green")
    ax.set_xlabel("Время (шаги)")
    ax.set_ylabel("Посещённая площадь (клеток)")
    ax.set_title("Посещённая площадь от времени")
    ax.grid(True, alpha=0.3)
    if path:
        fig.savefig(path, dpi=100, bbox_inches="tight")
        plt.close(fig)
    return fig


def create_gif(history, path, frame_step=50, fps=10):
    import imageio.v2 as imageio
    frames = []
    for t, grid in history:
        if t % frame_step != 0:
            continue
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(grid, cmap=CMAP_2, vmin=0, vmax=1, interpolation="nearest")
        ax.set_title(f"t = {t}", fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=70, bbox_inches="tight")
        buf.seek(0)
        frames.append(imageio.imread(buf))
        buf.close()
        plt.close(fig)
    imageio.mimsave(path, frames, fps=fps, loop=0)
    print(f"[visualize] GIF сохранён: {path}")


def create_multicolor_gif(history, path, q, frame_step=25, fps=10):
    import imageio.v2 as imageio
    cmap = _cmap_for_q(q)
    frames = []
    for t, grid in history:
        if t % frame_step != 0:
            continue
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(grid, cmap=cmap, vmin=0, vmax=q - 1, interpolation="nearest")
        ax.set_title(f"t = {t}", fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=70, bbox_inches="tight")
        buf.seek(0)
        frames.append(imageio.imread(buf))
        buf.close()
        plt.close(fig)
    imageio.mimsave(path, frames, fps=fps, loop=0)
    print(f"[visualize] GIF сохранён: {path}")


def create_multi_ant_gif(history, path, frame_step=25, fps=10):
    """GIF для L3: поле + позиции муравьёв."""
    import imageio.v2 as imageio
    frames = []
    for t, grid, positions in history:
        if t % frame_step != 0:
            continue
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(grid, cmap=CMAP_2, vmin=0, vmax=1, interpolation="nearest")
        for k, (i, j) in enumerate(positions):
            color = ANT_COLORS[k % len(ANT_COLORS)]
            ax.plot(j, i, marker="o", markersize=8,
                    markerfacecolor=color, markeredgecolor="white",
                    markeredgewidth=1.5)
        ax.set_title(f"t = {t}", fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=70, bbox_inches="tight")
        buf.seek(0)
        frames.append(imageio.imread(buf))
        buf.close()
        plt.close(fig)
    imageio.mimsave(path, frames, fps=fps, loop=0)
    print(f"[visualize] GIF сохранён: {path}")


def save_frame(history, t_target, path, q=2):
    if q == 2:
        cmap, vmax = CMAP_2, 1
    else:
        cmap, vmax = _cmap_for_q(q), q - 1

    for t, grid in history:
        if t == t_target:
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.imshow(grid, cmap=cmap, vmin=0, vmax=vmax, interpolation="nearest")
            ax.set_title(f"Шаг {t}", fontsize=12)
            ax.set_xticks([]); ax.set_yticks([])
            plt.tight_layout()
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"[visualize] Кадр сохранён: {path}")
            return
    print(f"[visualize] Шаг {t_target} не найден")