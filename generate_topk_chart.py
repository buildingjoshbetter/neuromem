#!/usr/bin/env python3
"""Generate the top_k diminishing returns chart for the research report."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = Path("/Users/j/Desktop/neuromem/charts")

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.titlesize': 15,
    'axes.labelsize': 13,
    'figure.facecolor': 'white',
    'axes.facecolor': '#FAFAFA',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

NEUROMEM_FC = "#2563EB"
ACCENT = "#10B981"
EVERMEMOS = "#F59E0B"

# Data: top_k values and recovery rates (50-question sample)
top_k_values = [15, 30, 50, 100, 200, 500]  # 500 = full context proxy
recovery_rates = [58.0, 68.0, 78.0, 82.0, 84.0, 92.0]

# Estimated full LoCoMo scores
# Base: 1114 correct. Failures: 357. Recovery adds recovered * (357/50) to base.
# More accurate: use the official scores where available
locomo_scores = [
    72.34 + (58.0/100 * 20.43),   # top_k=15
    72.34 + (68.0/100 * 20.43),   # top_k=30
    72.34 + (78.0/100 * 20.43),   # top_k=50
    72.34 + (82.0/100 * 20.43),   # top_k=100
    72.34 + (84.0/100 * 20.43),   # top_k=200
    93.81,                          # Full context (official)
]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# --- Left: Recovery rate vs top_k ---
ax1.plot(top_k_values, recovery_rates, 'o-', color=NEUROMEM_FC, linewidth=2.5, markersize=10)

for x, y in zip(top_k_values, recovery_rates):
    label = f'{y:.0f}%'
    if x == 500:
        label = f'{y:.0f}%\n(full ctx)'
    offset_y = 3 if y < 90 else -5
    ax1.annotate(label, xy=(x, y), xytext=(0, offset_y), textcoords='offset points',
                 ha='center', va='bottom' if offset_y > 0 else 'top',
                 fontweight='bold', fontsize=12)

# Mark the sweet spot
ax1.axvspan(80, 120, alpha=0.1, color=ACCENT)
ax1.annotate('Sweet spot\n(top_k=100)', xy=(100, 82), xytext=(250, 65),
             fontsize=11, style='italic', color=ACCENT, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=ACCENT, lw=2))

ax1.set_xlabel('top_k (retrieved documents)')
ax1.set_ylabel('Recovery Rate on 50 Failures (%)')
ax1.set_title('Diminishing Returns: Recovery vs Context Size', fontweight='bold')
ax1.set_xscale('log')
ax1.set_xticks(top_k_values)
ax1.set_xticklabels(['15', '30', '50', '100', '200', 'ALL'])
ax1.set_ylim(50, 100)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# --- Right: Estimated LoCoMo score vs top_k ---
ax2.plot(top_k_values, locomo_scores, 'o-', color=NEUROMEM_FC, linewidth=2.5, markersize=10)
ax2.axhline(y=92.77, color=EVERMEMOS, linestyle='--', linewidth=2, alpha=0.7,
            label='EverMemOS (92.77%)')

for x, y in zip(top_k_values, locomo_scores):
    label = f'{y:.1f}%'
    offset_y = 2
    if x == 500:
        label = f'{y:.1f}%\n(official)'
        offset_y = -4
    ax2.annotate(label, xy=(x, y), xytext=(0, offset_y), textcoords='offset points',
                 ha='center', va='bottom' if offset_y > 0 else 'top',
                 fontweight='bold', fontsize=11)

# Shade above EverMemOS
ax2.fill_between([10, 600], 92.77, 100, alpha=0.05, color=ACCENT)
ax2.text(20, 94.5, 'Beats EverMemOS', fontsize=10, color=ACCENT, fontweight='bold')

ax2.set_xlabel('top_k (retrieved documents)')
ax2.set_ylabel('Estimated LoCoMo Accuracy (%)')
ax2.set_title('Estimated Benchmark Score vs Context Size', fontweight='bold')
ax2.set_xscale('log')
ax2.set_xticks(top_k_values)
ax2.set_xticklabels(['15', '30', '50', '100', '200', 'ALL'])
ax2.set_ylim(80, 97)
ax2.legend(fontsize=11)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

fig.suptitle('Finding the Optimal Context Window: top_k Analysis',
             fontweight='bold', fontsize=16, y=1.02)
fig.tight_layout()
fig.savefig(OUT / '13_topk_diminishing_returns.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved: 13_topk_diminishing_returns.png")

# --- Per-category heatmap ---
fig, ax = plt.subplots(figsize=(10, 6))

categories = ['Cat 1\nSingle-hop', 'Cat 2\nMulti-hop', 'Cat 3\nTemporal', 'Cat 4\nOpen-domain']
top_ks = ['15', '30', '50', '100', '200', 'ALL']

data = np.array([
    [52.6, 57.1, 60.0, 63.2],   # top_k=15
    [63.2, 71.4, 80.0, 68.4],   # top_k=30
    [73.7, 85.7, 80.0, 78.9],   # top_k=50
    [73.7, 100.0, 80.0, 84.2],  # top_k=100
    [73.7, 85.7, 100.0, 89.5],  # top_k=200
    [94.7, 85.7, 80.0, 94.7],   # Full context
])

im = ax.imshow(data, cmap='YlGnBu', aspect='auto', vmin=40, vmax=100)

# Labels
ax.set_xticks(range(4))
ax.set_xticklabels(categories)
ax.set_yticks(range(6))
ax.set_yticklabels([f'top_k={k}' for k in top_ks])

# Add text annotations
for i in range(6):
    for j in range(4):
        val = data[i, j]
        color = 'white' if val > 80 else 'black'
        ax.text(j, i, f'{val:.1f}%', ha='center', va='center',
                fontweight='bold', fontsize=11, color=color)

ax.set_title('Per-Category Recovery Rates by top_k', fontweight='bold', pad=15)
fig.colorbar(im, ax=ax, label='Recovery Rate (%)', shrink=0.8)

fig.tight_layout()
fig.savefig(OUT / '14_topk_category_heatmap.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved: 14_topk_category_heatmap.png")
