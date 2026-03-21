#!/usr/bin/env python3
"""
Generate publication-quality charts for the Neuromem vs EverMemOS research report.
Charts cover: overall comparison, per-category breakdown, experiment progression,
diminishing returns, retrieval gap analysis, and failure distribution.
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Output directory
OUT = Path("/Users/j/Desktop/neuromem/charts")
OUT.mkdir(exist_ok=True)

# ─── Color palette ───
NEUROMEM_FC = "#2563EB"   # Blue - winning config
NEUROMEM_AG = "#60A5FA"   # Light blue - agentic
EVERMEMOS   = "#F59E0B"   # Amber/gold
NO_RETR     = "#94A3B8"   # Gray
ACCENT      = "#10B981"   # Green for highlights
DANGER      = "#EF4444"   # Red for failures

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.titlesize': 15,
    'axes.labelsize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'figure.facecolor': 'white',
    'axes.facecolor': '#FAFAFA',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

# ═══════════════════════════════════════════════════════════════════
# CHART 1: Overall Comparison Bar Chart
# ═══════════════════════════════════════════════════════════════════
def chart_overall_comparison():
    fig, ax = plt.subplots(figsize=(10, 6))

    systems = ['No Retrieval', 'Neuromem\n(Agentic)', 'EverMemOS', 'Neuromem\n(Full Context)']
    scores = [5.67, 72.34, 92.77, 93.81]
    colors = [NO_RETR, NEUROMEM_AG, EVERMEMOS, NEUROMEM_FC]

    bars = ax.bar(systems, scores, color=colors, width=0.6, edgecolor='white', linewidth=1.5)

    # Add value labels on bars
    for bar, score in zip(bars, scores):
        ypos = bar.get_height() + 1
        ax.text(bar.get_x() + bar.get_width()/2, ypos, f'{score:.2f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=14)

    # Winner annotation
    ax.annotate('WINNER', xy=(3, 93.81), xytext=(3, 98),
                ha='center', fontsize=11, fontweight='bold', color=ACCENT,
                arrowprops=dict(arrowstyle='->', color=ACCENT, lw=2))

    # EverMemOS baseline line
    ax.axhline(y=92.77, color=EVERMEMOS, linestyle='--', alpha=0.5, linewidth=1.5)
    ax.text(0.02, 93.5, 'EverMemOS baseline (92.77%)', transform=ax.get_yaxis_transform(),
            fontsize=9, color=EVERMEMOS, alpha=0.8)

    ax.set_ylabel('LoCoMo Accuracy (%)')
    ax.set_title('LoCoMo Benchmark: Overall Accuracy Comparison', fontweight='bold', pad=15)
    ax.set_ylim(0, 105)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / '01_overall_comparison.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 01_overall_comparison.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 2: Per-Category Grouped Bar Chart
# ═══════════════════════════════════════════════════════════════════
def chart_category_comparison():
    fig, ax = plt.subplots(figsize=(12, 7))

    categories = ['Cat 1\nSingle-hop', 'Cat 2\nMulti-hop', 'Cat 3\nTemporal', 'Cat 4\nOpen-domain']

    nm_ag  = [59.2, 72.9, 52.1, 79.0]   # Neuromem agentic
    em     = [91.1, 89.4, 78.1, 96.2]   # EverMemOS
    nm_fc  = [93.03, 91.90, 78.82, 96.51]  # Neuromem full context

    x = np.arange(len(categories))
    w = 0.25

    bars1 = ax.bar(x - w, nm_ag, w, label='Neuromem (Agentic)', color=NEUROMEM_AG, edgecolor='white')
    bars2 = ax.bar(x,     em,    w, label='EverMemOS', color=EVERMEMOS, edgecolor='white')
    bars3 = ax.bar(x + w, nm_fc, w, label='Neuromem (Full Context)', color=NEUROMEM_FC, edgecolor='white')

    # Value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.8, f'{h:.1f}%',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_ylabel('Accuracy (%)')
    ax.set_title('Per-Category Accuracy Breakdown', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 108)
    ax.legend(loc='upper left', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / '02_category_comparison.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 02_category_comparison.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 3: Experiment Progression (Diminishing Returns)
# ═══════════════════════════════════════════════════════════════════
def chart_experiment_progression():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # --- Left panel: Recovery rate on 50-question sample ---
    exps_50 = [
        ('Baseline\n(agentic)', 40.0),
        ('Top-k=30', 40.0),
        ('Sonnet\n(OpenRouter)', 36.0),
        ('Opus\n(OpenRouter)', 54.0),
        ('Structured\nPrompt', 56.0),
        ('Full Context\n(Sonnet)', 54.0),
        ('Full Context\n(GPT-4.1-mini)', 92.0),
    ]
    names_50 = [e[0] for e in exps_50]
    rates_50 = [e[1] for e in exps_50]

    colors_50 = [NEUROMEM_AG] * 5 + [NEUROMEM_FC, NEUROMEM_FC]
    colors_50[-1] = ACCENT  # Highlight winner

    bars = ax1.barh(range(len(exps_50)), rates_50, color=colors_50, edgecolor='white', height=0.6)
    for i, (bar, rate) in enumerate(zip(bars, rates_50)):
        ax1.text(rate + 1.5, i, f'{rate:.0f}%', va='center', fontweight='bold', fontsize=11)

    ax1.set_yticks(range(len(exps_50)))
    ax1.set_yticklabels(names_50)
    ax1.set_xlabel('Recovery Rate (%)')
    ax1.set_title('50-Question Sample: Recovery Rates', fontweight='bold')
    ax1.set_xlim(0, 105)
    ax1.invert_yaxis()
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # --- Right panel: Full 357-question results ---
    exps_357 = [
        ('Baseline\n(agentic)', 30.3),
        ('Structured\nPrompt', 48.7),
        ('Full Context\n(GPT-4.1-mini)', 92.4),
    ]
    names_357 = [e[0] for e in exps_357]
    rates_357 = [e[1] for e in exps_357]

    colors_357 = [NEUROMEM_AG, NEUROMEM_AG, ACCENT]

    bars = ax2.barh(range(len(exps_357)), rates_357, color=colors_357, edgecolor='white', height=0.5)
    for i, (bar, rate) in enumerate(zip(bars, rates_357)):
        ax2.text(rate + 1.5, i, f'{rate:.1f}%', va='center', fontweight='bold', fontsize=13)

    ax2.set_yticks(range(len(exps_357)))
    ax2.set_yticklabels(names_357)
    ax2.set_xlabel('Recovery Rate (%)')
    ax2.set_title('Full 357-Question Test: Recovery Rates', fontweight='bold')
    ax2.set_xlim(0, 105)
    ax2.invert_yaxis()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    fig.suptitle('Experiment Progression: Finding the Optimal Configuration',
                 fontweight='bold', fontsize=16, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / '03_experiment_progression.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 03_experiment_progression.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 4: Retrieval Gap Waterfall
# ═══════════════════════════════════════════════════════════════════
def chart_retrieval_gap():
    fig, ax = plt.subplots(figsize=(12, 6))

    # Waterfall showing: Agentic → Prompt → Full Context → Winner
    stages = ['Neuromem\nAgentic', '+Structured\nPrompt', '+Full Context\nMode', 'Neuromem FC\n(Official)']
    values = [72.34, 83.7, 93.8, 93.81]
    increments = [72.34, 83.7-72.34, 93.8-83.7, 93.81-93.8]

    bottoms = [0, 72.34, 83.7, 0]
    colors_wf = [NEUROMEM_AG, '#818CF8', NEUROMEM_FC, ACCENT]

    # Draw bars
    for i, (stage, val, inc, bot) in enumerate(zip(stages, values, increments, bottoms)):
        if i == 3:  # Final total bar
            ax.bar(i, val, color=ACCENT, edgecolor='white', width=0.5, alpha=0.9)
            ax.text(i, val + 1, f'{val:.2f}%', ha='center', fontweight='bold', fontsize=13, color=ACCENT)
        else:
            ax.bar(i, inc, bottom=bot, color=colors_wf[i], edgecolor='white', width=0.5, alpha=0.9)
            ax.text(i, val + 1, f'{val:.1f}%', ha='center', fontweight='bold', fontsize=12)
            if i > 0:
                ax.text(i, bot + inc/2, f'+{inc:.1f}pp', ha='center', fontsize=10,
                        color='white', fontweight='bold')

    # Connector lines
    for i in range(2):
        ax.plot([i + 0.25, i + 0.75], [values[i], values[i]], color='gray',
                linestyle='--', linewidth=1, alpha=0.5)

    # EverMemOS line
    ax.axhline(y=92.77, color=EVERMEMOS, linestyle='--', linewidth=2, alpha=0.7)
    ax.text(3.4, 92.77, 'EverMemOS (92.77%)', fontsize=10, color=EVERMEMOS,
            fontweight='bold', va='center')

    ax.set_xticks(range(4))
    ax.set_xticklabels(stages)
    ax.set_ylabel('LoCoMo Accuracy (%)')
    ax.set_title('Closing the Gap: From 72% to 94%', fontweight='bold', pad=15)
    ax.set_ylim(0, 102)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / '04_retrieval_gap_waterfall.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 04_retrieval_gap_waterfall.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 5: Failure Category Pie + Bar
# ═══════════════════════════════════════════════════════════════════
def chart_failure_analysis():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- Left: Failure categories (agentic search) ---
    cats = ['Retrieval\nMiss', 'Temporal', 'Multi-hop', 'Insufficient\nDetail', 'Wrong\nInference', 'Vocab\nMismatch']
    counts = [107, 89, 68, 57, 25, 11]
    colors_pie = ['#EF4444', '#F59E0B', '#8B5CF6', '#3B82F6', '#10B981', '#94A3B8']

    wedges, texts, autotexts = ax1.pie(counts, labels=cats, colors=colors_pie, autopct='%1.0f%%',
                                        startangle=90, textprops={'fontsize': 10})
    for t in autotexts:
        t.set_fontweight('bold')
        t.set_fontsize(11)
    ax1.set_title('Agentic Search Failure Categories\n(357 failures)', fontweight='bold')

    # --- Right: Category recovery rates (full context vs agentic) ---
    cat_names = ['Cat 1\nSingle-hop', 'Cat 2\nMulti-hop', 'Cat 3\nTemporal', 'Cat 4\nOpen-domain']
    agentic_correct = [167, 234, 50, 664]
    fc_correct = [262, 295, 76, 812]
    total_per_cat = [282, 321, 96, 841]

    agentic_pct = [c/t*100 for c,t in zip(agentic_correct, total_per_cat)]
    fc_pct = [c/t*100 for c,t in zip(fc_correct, total_per_cat)]
    gap = [f - a for f, a in zip(fc_pct, agentic_pct)]

    x = np.arange(len(cat_names))
    w = 0.35

    ax2.bar(x - w/2, agentic_pct, w, label='Agentic (72.3%)', color=NEUROMEM_AG, edgecolor='white')
    ax2.bar(x + w/2, fc_pct, w, label='Full Context (93.8%)', color=NEUROMEM_FC, edgecolor='white')

    # Gap annotations
    for i, g in enumerate(gap):
        ax2.annotate(f'+{g:.0f}pp', xy=(i + w/2, fc_pct[i]), xytext=(i + 0.5, fc_pct[i] - 5),
                     fontsize=10, fontweight='bold', color=ACCENT,
                     arrowprops=dict(arrowstyle='->', color=ACCENT, lw=1.5))

    ax2.set_ylabel('Accuracy (%)')
    ax2.set_title('Category Recovery: Agentic vs Full Context', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(cat_names)
    ax2.set_ylim(0, 110)
    ax2.legend(loc='upper left')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / '05_failure_analysis.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 05_failure_analysis.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 6: Diminishing Returns Curve
# ═══════════════════════════════════════════════════════════════════
def chart_diminishing_returns():
    fig, ax = plt.subplots(figsize=(12, 7))

    # All experiments ordered by estimated LoCoMo score
    experiments = [
        ('No Retrieval', 5.67, '$0', NO_RETR),
        ('Neuromem Neutral', 66.10, '~$0.02/q', NEUROMEM_AG),
        ('Neuromem Agentic', 72.34, '~$0.03/q', NEUROMEM_AG),
        ('+ Structured Prompt', 83.7, '~$0.04/q', '#818CF8'),
        ('EverMemOS Neutral', 86.88, '~$0.15/q', EVERMEMOS),
        ('EverMemOS', 92.77, '~$0.20/q', EVERMEMOS),
        ('Neuromem FC', 93.81, '~$0.05/q', NEUROMEM_FC),
    ]

    names = [e[0] for e in experiments]
    scores = [e[1] for e in experiments]
    costs = [e[2] for e in experiments]
    colors_dr = [e[3] for e in experiments]

    # Plot curve
    ax.plot(range(len(experiments)), scores, 'o-', color='#6B7280', linewidth=2, markersize=10, zorder=2)

    # Colored scatter on top
    for i, (name, score, cost, color) in enumerate(experiments):
        ax.scatter(i, score, color=color, s=200, zorder=3, edgecolor='white', linewidth=2)

        # Label
        offset_y = 4 if i % 2 == 0 else -6
        va = 'bottom' if i % 2 == 0 else 'top'
        ax.annotate(f'{name}\n{score:.1f}%', xy=(i, score),
                    xytext=(0, offset_y), textcoords='offset points',
                    ha='center', va=va, fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, alpha=0.9))

    # Shaded regions
    ax.axhspan(0, 72.34, alpha=0.05, color=DANGER, label='Below Neuromem Agentic')
    ax.axhspan(72.34, 92.77, alpha=0.05, color=EVERMEMOS, label='Retrieval Gap Zone')
    ax.axhspan(92.77, 100, alpha=0.05, color=ACCENT, label='Beating EverMemOS')

    # EverMemOS line
    ax.axhline(y=92.77, color=EVERMEMOS, linestyle='--', linewidth=1.5, alpha=0.5)

    ax.set_ylabel('LoCoMo Accuracy (%)')
    ax.set_xlabel('Experiment (ordered by score)')
    ax.set_title('Diminishing Returns: Score vs. Approach Complexity', fontweight='bold', pad=15)
    ax.set_ylim(0, 102)
    ax.set_xticks([])
    ax.legend(loc='lower right', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / '06_diminishing_returns.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 06_diminishing_returns.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 7: Architecture Comparison Radar
# ═══════════════════════════════════════════════════════════════════
def chart_architecture_radar():
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    categories = ['Single-hop\nAccuracy', 'Multi-hop\nAccuracy', 'Temporal\nAccuracy',
                   'Open-domain\nAccuracy', 'Cost\nEfficiency', 'Simplicity']
    N = len(categories)

    # Scores (normalized 0-100)
    evermemos = [91.1, 89.4, 78.1, 96.2, 30, 20]    # Low cost/simplicity (heavy infra)
    nm_fc =     [93.03, 91.90, 78.82, 96.51, 80, 95]  # High efficiency, simple
    nm_ag =     [59.2, 72.9, 52.1, 79.0, 95, 70]     # Cheapest per-query

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    for vals, label, color in [(evermemos, 'EverMemOS', EVERMEMOS),
                                 (nm_fc, 'Neuromem FC', NEUROMEM_FC),
                                 (nm_ag, 'Neuromem Agentic', NEUROMEM_AG)]:
        vals_closed = vals + vals[:1]
        ax.plot(angles, vals_closed, 'o-', linewidth=2, label=label, color=color)
        ax.fill(angles, vals_closed, alpha=0.1, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_title('Architecture Trade-offs', fontweight='bold', pad=25, fontsize=14)
    ax.legend(loc='lower right', bbox_to_anchor=(1.3, -0.05), fontsize=10)

    fig.tight_layout()
    fig.savefig(OUT / '07_architecture_radar.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 07_architecture_radar.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 8: Answer Model Comparison
# ═══════════════════════════════════════════════════════════════════
def chart_answer_model_comparison():
    fig, ax = plt.subplots(figsize=(10, 6))

    # Recovery rates on 50-question failure sample with different answer models
    models = ['Opus 4.6\n(direct API)', 'Sonnet 4.5\n(direct API)', 'Sonnet 4.5\n(OpenRouter)',
              'Opus 4.6\n(OpenRouter)', 'GPT-4.1-mini\n(OpenRouter)']
    rates = [0.0, 0.0, 36.0, 54.0, 92.0]
    colors_m = [DANGER, DANGER, NEUROMEM_AG, NEUROMEM_AG, ACCENT]

    bars = ax.barh(range(len(models)), rates, color=colors_m, edgecolor='white', height=0.5)

    for i, (bar, rate) in enumerate(zip(bars, rates)):
        if rate == 0:
            ax.text(3, i, f'{rate:.0f}% (API auth failure)', va='center', fontsize=11,
                    color=DANGER, fontweight='bold')
        else:
            ax.text(rate + 1.5, i, f'{rate:.0f}%', va='center', fontsize=12, fontweight='bold')

    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models)
    ax.set_xlabel('Recovery Rate on 50 Failure Questions (%)')
    ax.set_title('Answer Model Impact: Full Context Mode', fontweight='bold', pad=15)
    ax.set_xlim(0, 105)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Annotation
    ax.annotate('GPT-4.1-mini: Best balance of\ncost, speed, and accuracy',
                xy=(92, 4), xytext=(55, 2.5),
                fontsize=10, style='italic', color='#4B5563',
                arrowprops=dict(arrowstyle='->', color='#4B5563'))

    fig.tight_layout()
    fig.savefig(OUT / '08_answer_model_comparison.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 08_answer_model_comparison.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 9: Head-to-Head Delta Chart
# ═══════════════════════════════════════════════════════════════════
def chart_head_to_head():
    fig, ax = plt.subplots(figsize=(10, 5))

    categories = ['Overall', 'Cat 1\nSingle-hop', 'Cat 2\nMulti-hop',
                   'Cat 3\nTemporal', 'Cat 4\nOpen-domain']
    nm_fc = [93.81, 93.03, 91.90, 78.82, 96.51]
    em    = [92.77, 91.10, 89.40, 78.10, 96.20]
    deltas = [n - e for n, e in zip(nm_fc, em)]

    colors_d = [ACCENT if d > 0 else DANGER for d in deltas]

    bars = ax.bar(categories, deltas, color=colors_d, width=0.5, edgecolor='white', linewidth=1.5)

    for bar, delta in zip(bars, deltas):
        ypos = delta + 0.05 if delta > 0 else delta - 0.05
        va = 'bottom' if delta > 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2, ypos, f'+{delta:.2f}pp',
                ha='center', va=va, fontweight='bold', fontsize=13, color=ACCENT)

    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.set_ylabel('Neuromem FC - EverMemOS (pp)')
    ax.set_title('Head-to-Head: Neuromem FC vs EverMemOS\n(positive = Neuromem wins)',
                 fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # All positive - add banner
    ax.text(0.98, 0.95, 'Neuromem wins ALL categories', transform=ax.transAxes,
            fontsize=12, fontweight='bold', color=ACCENT, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#ECFDF5', edgecolor=ACCENT))

    fig.tight_layout()
    fig.savefig(OUT / '09_head_to_head_delta.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 09_head_to_head_delta.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 10: Cost vs Accuracy Scatter
# ═══════════════════════════════════════════════════════════════════
def chart_cost_vs_accuracy():
    fig, ax = plt.subplots(figsize=(10, 7))

    # Approximate cost per question (answer generation only, USD)
    systems = [
        ('No Retrieval', 5.67, 0.001, NO_RETR, 100),
        ('Neuromem Agentic', 72.34, 0.03, NEUROMEM_AG, 200),
        ('Neuromem + Prompt', 83.7, 0.04, '#818CF8', 200),
        ('EverMemOS (Neutral)', 86.88, 0.15, EVERMEMOS, 200),
        ('EverMemOS', 92.77, 0.20, EVERMEMOS, 300),
        ('Neuromem FC', 93.81, 0.05, NEUROMEM_FC, 350),
    ]

    for name, acc, cost, color, size in systems:
        ax.scatter(cost, acc, c=color, s=size, edgecolor='white', linewidth=2, zorder=3)
        offset_x = 0.005
        offset_y = 1.5
        if name == 'EverMemOS':
            offset_y = -3
        ax.annotate(name, xy=(cost, acc), xytext=(cost + offset_x, acc + offset_y),
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, alpha=0.8))

    # Pareto frontier
    ax.plot([0.001, 0.03, 0.05], [5.67, 72.34, 93.81], '--', color=ACCENT, alpha=0.4, linewidth=2)

    # Highlight Neuromem FC as best value
    ax.annotate('Best value:\nHighest accuracy,\nlow cost', xy=(0.05, 93.81),
                xytext=(0.12, 88), fontsize=10, style='italic', color=ACCENT,
                arrowprops=dict(arrowstyle='->', color=ACCENT, lw=2))

    ax.set_xlabel('Estimated Cost per Question (USD)')
    ax.set_ylabel('LoCoMo Accuracy (%)')
    ax.set_title('Cost-Effectiveness: Accuracy vs. Cost per Question', fontweight='bold', pad=15)
    ax.set_ylim(0, 102)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / '10_cost_vs_accuracy.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 10_cost_vs_accuracy.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 11: Consistency Across Runs
# ═══════════════════════════════════════════════════════════════════
def chart_consistency():
    fig, ax = plt.subplots(figsize=(8, 5))

    # 3-run results
    runs = [1, 2, 3]
    nm_fc_runs = [93.77, 93.70, 93.96]
    em_baseline = 92.77

    ax.plot(runs, nm_fc_runs, 'o-', color=NEUROMEM_FC, linewidth=2, markersize=12,
            label='Neuromem FC', zorder=3)
    ax.fill_between(runs, min(nm_fc_runs) - 0.2, max(nm_fc_runs) + 0.2,
                     color=NEUROMEM_FC, alpha=0.1)

    ax.axhline(y=em_baseline, color=EVERMEMOS, linestyle='--', linewidth=2,
               label=f'EverMemOS ({em_baseline}%)')

    for i, v in enumerate(nm_fc_runs):
        ax.text(runs[i], v + 0.15, f'{v:.2f}%', ha='center', fontweight='bold', fontsize=12)

    ax.set_xlabel('Judge Run')
    ax.set_ylabel('Accuracy (%)')
    ax.set_title('Consistency Across 3 Judge Runs', fontweight='bold', pad=15)
    ax.set_xticks(runs)
    ax.set_ylim(92, 95)
    ax.legend(fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Std annotation
    mean_acc = np.mean(nm_fc_runs)
    std_acc = np.std(nm_fc_runs)
    ax.text(0.98, 0.05, f'Mean: {mean_acc:.2f}% ± {std_acc:.2f}%',
            transform=ax.transAxes, fontsize=11, ha='right',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#EFF6FF', edgecolor=NEUROMEM_FC))

    fig.tight_layout()
    fig.savefig(OUT / '11_consistency.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 11_consistency.png")

# ═══════════════════════════════════════════════════════════════════
# CHART 12: Infrastructure Comparison
# ═══════════════════════════════════════════════════════════════════
def chart_infrastructure():
    fig, ax = plt.subplots(figsize=(10, 6))

    metrics = ['External\nDatabases', 'LLM Calls\nper Message\n(Ingestion)',
               'Embedding\nModel Size', 'Monthly\nInfra Cost', 'Accuracy']

    # Normalized to 0-100 scale (lower = simpler/cheaper/better for first 4, higher = better for accuracy)
    em_vals  = [85, 90, 80, 90, 93]  # MongoDB+Redis+Elastic+Milvus, 17 prompts, Qwen 4B, $$$$
    nm_vals  = [5, 15, 10, 5, 94]    # SQLite only, ~1-2 prompts, Model2Vec 8M, ~$0

    x = np.arange(len(metrics))
    w = 0.35

    bars1 = ax.bar(x - w/2, em_vals, w, label='EverMemOS', color=EVERMEMOS, edgecolor='white')
    bars2 = ax.bar(x + w/2, nm_vals, w, label='Neuromem FC', color=NEUROMEM_FC, edgecolor='white')

    # Labels for what the numbers mean
    em_labels = ['MongoDB, Redis,\nElastic, Milvus', '17 prompts/msg', 'Qwen3-4B\n(4GB GPU)', '~$50-100/mo', '92.77%']
    nm_labels = ['SQLite\n(1 file)', '~1-2 prompts/msg', 'Model2Vec\n(32MB CPU)', '~$0/mo', '93.81%']

    for i, (bar, lbl) in enumerate(zip(bars1, em_labels)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, lbl,
                ha='center', va='bottom', fontsize=7.5, color='#6B7280')
    for i, (bar, lbl) in enumerate(zip(bars2, nm_labels)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, lbl,
                ha='center', va='bottom', fontsize=7.5, color='#374151')

    ax.set_ylabel('Complexity/Cost Score (lower = simpler)')
    ax.set_title('Infrastructure Comparison: Complexity vs Performance', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 115)
    ax.legend(loc='upper left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Note for last column
    ax.annotate('Higher = better\nfor accuracy', xy=(4, 94), xytext=(4.3, 80),
                fontsize=8, style='italic', color='#6B7280',
                arrowprops=dict(arrowstyle='->', color='#6B7280', lw=1))

    fig.tight_layout()
    fig.savefig(OUT / '12_infrastructure_comparison.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: 12_infrastructure_comparison.png")

# ═══════════════════════════════════════════════════════════════════
# RUN ALL
# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("Generating Neuromem Research Charts...")
    print(f"Output directory: {OUT}\n")

    chart_overall_comparison()
    chart_category_comparison()
    chart_experiment_progression()
    chart_retrieval_gap()
    chart_failure_analysis()
    chart_diminishing_returns()
    chart_architecture_radar()
    chart_answer_model_comparison()
    chart_head_to_head()
    chart_cost_vs_accuracy()
    chart_consistency()
    chart_infrastructure()

    print(f"\nDone! {len(list(OUT.glob('*.png')))} charts generated in {OUT}/")
