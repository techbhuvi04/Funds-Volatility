import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from pathlib import Path
ROOT = Path(__file__).resolve().parent
D = str(ROOT / "data") + "/"
F = str(ROOT / "figures") + "/"
(ROOT / "figures").mkdir(exist_ok=True)
BENCH = "Nifty 500 (index fund)"
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#9a998f", "#e6e5e0", "#fcfcfb"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "figure.facecolor": SURF, "axes.facecolor": SURF,
    "savefig.dpi": 200, "savefig.bbox": "tight"})

M = pd.read_csv(D + "metrics.csv", index_col=0)
E = pd.read_csv(D + "extra.csv", index_col=0)
dd = pd.read_csv(D + "drawdowns.csv", index_col=0, parse_dates=True)
R = pd.read_csv(D + "ranks.csv", index_col=0)
O = pd.read_csv(D + "oos.csv", index_col=0)
funds = [f for f in M.index if f != BENCH]

# 1. Drawdown curves, three funds highlighted
fig, ax = plt.subplots(figsize=(10, 4.6))
hl = {"UTI": ORANGE, "HDFC": BLUE, "Parag Parikh": AQUA}
for f in funds:
    if f not in hl: ax.plot(dd.index, dd[f] * 100, color="#c9c8c0", lw=0.9, zorder=1)
ax.plot(dd.index, dd[BENCH] * 100, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=2)
for f, c in hl.items(): ax.plot(dd.index, dd[f] * 100, color=c, lw=2, zorder=3)
ax.set_ylabel("Drawdown from previous peak (%)"); ax.set_ylim(-42, 1)
ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
from matplotlib.lines import Line2D
h = [Line2D([], [], color=c, lw=2, label=f) for f, c in hl.items()] + [Line2D([], [], color=INK, lw=1.2, ls=(0, (4, 3)), label="Nifty 500 index fund"), Line2D([], [], color="#c9c8c0", lw=1, label="Other 5 funds")]
ax.legend(handles=h, loc="lower right", frameon=False, ncol=5, fontsize=9, bbox_to_anchor=(1, -0.2))
ax.set_title("Drawdowns, Nov 2019 - Oct 2026", loc="left", color=INK, fontsize=12, fontweight="bold")
fig.savefig(F + "fig1_drawdowns.png"); plt.close(fig)

def label_scatter(ax, x, y, names, offsets=None):
    offsets = offsets or {}
    for n, xi, yi in zip(names, x, y):
        dx, dy = offsets.get(n, (6, 4))
        ax.annotate(n, (xi, yi), xytext=(dx, dy), textcoords="offset points", fontsize=9, color=INK)

# 2. SD vs post-2021 max drawdown
fig, ax = plt.subplots(figsize=(6.4, 4.6))
x = M.loc[funds, "vol"] * 100; y = E.loc[funds, "mdd_post2021"] * 100
ax.scatter(x, y, s=60, color=BLUE, edgecolor=SURF, linewidth=2, zorder=3)
ax.scatter(M.loc[BENCH, "vol"] * 100, E.loc[BENCH, "mdd_post2021"] * 100, s=60, marker="D", color=INK, zorder=3)
label_scatter(ax, list(x) + [M.loc[BENCH, "vol"] * 100], list(y) + [E.loc[BENCH, "mdd_post2021"] * 100], funds + ["Nifty 500"],
              {"Franklin India": (6, 6), "Kotak": (8, 2), "Canara Robeco": (-30, -14), "Nifty 500": (8, -12), "Parag Parikh": (6, -4)})
ax.set_xlabel("Annualised standard deviation, full period (%)"); ax.set_ylabel("Worst drawdown since Jan 2021 (%)")
ax.set_title("Low SD did not mean shallow post-COVID falls", loc="left", color=INK, fontsize=12, fontweight="bold")
fig.savefig(F + "fig2_sd_vs_dd.png"); plt.close(fig)

# 3. Up vs down capture
fig, ax = plt.subplots(figsize=(6.4, 4.6))
x = M.loc[funds, "down_capture"] * 100; y = M.loc[funds, "up_capture"] * 100
ax.axline((50, 50), (100, 100), color=MUTED, lw=1, ls=(0, (4, 3)))
ax.scatter(x, y, s=60, color=BLUE, edgecolor=SURF, linewidth=2, zorder=3)
label_scatter(ax, x, y, funds, {"Motilal Oswal": (8, 2), "UTI": (6, -10), "Kotak": (-40, -3), "Canara Robeco": (-82, -4), "HDFC": (-34, 4)})
ax.text(60, 57, "up = down", color=MUTED, fontsize=8, ha="right")
ax.set_xlabel("Downside capture vs Nifty 500 (%)  ← better"); ax.set_ylabel("Upside capture vs Nifty 500 (%)")
ax.set_title("Monthly capture ratios, Nov 2019 - Oct 2026", loc="left", color=INK, fontsize=12, fontweight="bold")
fig.savefig(F + "fig3_capture.png"); plt.close(fig)

# 4. Rank heatmap
order = R.sort_values("SD").index
Rm = R.loc[order]
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("b", ["#cde2fb", "#6da7ec", "#256abf", "#0d366b"])
fig, ax = plt.subplots(figsize=(8, 4.4)); ax.grid(False)
ax.imshow(Rm.values, cmap=cmap, vmin=1, vmax=8, aspect="auto")
for i in range(Rm.shape[0]):
    for j in range(Rm.shape[1]):
        v = Rm.values[i, j]; ax.text(j, i, v, ha="center", va="center", color=INK if v <= 4 else "white", fontsize=10)
ax.set_xticks(range(Rm.shape[1]), [x.replace(" ", "\n", 1) for x in Rm.columns], fontsize=9); ax.set_yticks(range(len(order)), order)
ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
ax.xaxis.tick_top()
ax.set_title("Risk rank by metric (1 = safest), sorted by SD", loc="left", color=INK, fontsize=12, fontweight="bold", pad=28)
fig.savefig(F + "fig4_rank_heatmap.png"); plt.close(fig)

# 5. Out-of-sample: H1 vol vs H2 drawdown
fig, ax = plt.subplots(figsize=(6.4, 4.6))
x = O["vol_H1"] * 100; y = O["mdd_H2"] * 100
ax.scatter(x, y, s=60, color=BLUE, edgecolor=SURF, linewidth=2, zorder=3)
label_scatter(ax, x, y, O.index, {"Kotak": (6, -10), "Franklin India": (6, 4), "Motilal Oswal": (-30, 8), "Canara Robeco": (6, -4)})
ax.set_xlabel("SD, Nov 2019 - Oct 2022 (%)"); ax.set_ylabel("Max drawdown, Nov 2022 - Oct 2026 (%)")
ax.set_title("Past volatility vs future drawdown", loc="left", color=INK, fontsize=12, fontweight="bold")
fig.savefig(F + "fig5_oos.png"); plt.close(fig)
print("done")
