#!/usr/bin/env python3
"""
Generate deep analysis charts for Neuromem — March 23, 2026.

Produces ~12 PNGs for the NEUROMEM_DEEP_ANALYSIS.md synthesis document.
Style: ADHD-friendly, high contrast, cream background, clear labels.
Follows the established convention from /charts/generate_architecture_charts.py.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.patheffects as pe
import numpy as np
import os

CHARTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Color palette (matches existing charts) ──────────────────────────────
C = {
    'neuromem':   '#3498db',   # Blue — Neuromem
    'evermemos':  '#e67e22',   # Orange — EverMemOS
    'target':     '#2ecc71',   # Green — target/goal
    'ceiling':    '#9b59b6',   # Purple — full context ceiling
    'danger':     '#e74c3c',   # Red — problem/gap
    'amber':      '#f39c12',   # Amber — caution/partial
    'bg':         '#faf9f6',   # Cream background
    'grid':       '#e0e0e0',
    'text':       '#2c3e50',   # Dark blue-gray text
    'dark':       '#34495e',
    'light_blue': '#85c1e9',
    'light_green':'#82e0aa',
    'light_purple':'#c39bd3',
    'light_orange':'#f0b27a',
    'teal':       '#1abc9c',
    'pink':       '#e91e63',
    'indigo':     '#5c6bc0',
}

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.facecolor': C['bg'],
    'figure.facecolor': C['bg'],
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.color': C['grid'],
    'axes.spines.top': False,
    'axes.spines.right': False,
    'text.color': C['text'],
    'axes.labelcolor': C['text'],
    'xtick.color': C['text'],
    'ytick.color': C['text'],
})


# ═══════════════════════════════════════════════════════════════════════════
# Chart 1: The Journey — Score Progression Waterfall
# ═══════════════════════════════════════════════════════════════════════════

def chart_01_score_progression():
    """Bar chart: v2 → v3 → Phase0 → Phase1 → EverMemOS → FC → Target."""
    fig, ax = plt.subplots(figsize=(14, 7))

    labels = [
        'Neuromem v2\n(Mar 19)',
        'Neuromem v3\n(Mar 19)',
        'Phase 0\nReranker\nUpgrade',
        'Phase 1\nEmbed +\nReranker',
        'EverMemOS\n(Their Best)',
        'Full Context\nCeiling',
        'Target\n(Goal)',
    ]
    scores = [72.34, 87.71, 90.81, 91.21, 92.77, 93.81, 96.0]
    colors = [
        C['light_blue'],   # v2 — faded
        C['neuromem'],     # v3
        C['neuromem'],     # Phase 0
        C['neuromem'],     # Phase 1
        C['evermemos'],    # EverMemOS
        C['ceiling'],      # FC
        C['target'],       # Target
    ]

    x = np.arange(len(labels))
    bars = ax.bar(x, scores, color=colors, edgecolor='white', linewidth=2.5,
                  width=0.65, alpha=0.9, zorder=3)

    # Score labels on bars
    for i, (bar, score) in enumerate(zip(bars, scores)):
        y_pos = score + 0.8
        label = f"{score:.2f}%"
        if i == 6:
            label = f"~{score:.0f}%+"
        fontsize = 13 if i in [3, 4, 6] else 11
        weight = 'bold' if i in [3, 4, 6] else 'normal'
        ax.text(i, y_pos, label, ha='center', va='bottom', fontsize=fontsize,
                fontweight=weight, color=C['text'], zorder=5)

    # Delta annotations between key bars
    deltas = [
        (0, 1, '+15.37pp', C['target']),
        (1, 2, '+3.10pp', C['target']),
        (2, 3, '+0.40pp', C['amber']),
        (3, 4, '-1.56pp\nGAP', C['danger']),
    ]
    for start, end, label, color in deltas:
        mid_x = (start + end) / 2
        mid_y = max(scores[start], scores[end]) + 3.5
        ax.annotate('', xy=(end, scores[end] + 1.5), xytext=(start, scores[start] + 1.5),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2),
                    zorder=4)
        ax.text(mid_x, mid_y, label, ha='center', va='bottom', fontsize=9,
                fontweight='bold', color=color)

    # EverMemOS reference line
    ax.axhline(y=92.77, color=C['evermemos'], linestyle='--', alpha=0.4, linewidth=1.5, zorder=1)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel('LoCoMo Accuracy (%)', fontsize=13, fontweight='bold')
    ax.set_ylim(65, 102)
    ax.set_title('The Journey So Far: From 72% to 91% — And Where We\'re Going',
                fontsize=15, fontweight='bold', pad=20)

    # Insight box
    insight = "Each jump required a different kind of innovation.\nModel swaps are exhausted. The next jump needs algorithmic breakthroughs."
    ax.text(0.02, 0.02, insight, transform=ax.transAxes, fontsize=10,
            style='italic', color=C['dark'], va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=C['target'], alpha=0.08))

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_01_score_progression.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [1/12] Score progression")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 2: The Remaining Gap — Where Points Live
# ═══════════════════════════════════════════════════════════════════════════

def chart_02_the_gap():
    """Horizontal number line showing where we are and where we need to go."""
    fig, ax = plt.subplots(figsize=(14, 5))

    # Number line from 88 to 98
    ax.set_xlim(87, 98.5)
    ax.set_ylim(-2, 6)
    ax.axhline(y=0, color=C['dark'], linewidth=3, zorder=2)
    ax.axis('off')

    # Tick marks
    for x in range(88, 99):
        ax.plot([x, x], [-0.15, 0.15], color=C['dark'], linewidth=1.5, zorder=3)
        ax.text(x, -0.6, f"{x}%", ha='center', fontsize=9, color=C['text'])

    # Markers
    markers = [
        (91.21, 'Neuromem\nPhase 1', C['neuromem'], 2.5, 16),
        (92.77, 'EverMemOS', C['evermemos'], 2.5, 16),
        (93.81, 'Full Context\nCeiling', C['ceiling'], 2.5, 14),
        (96.0, 'Target\n96%+', C['target'], 2.5, 16),
    ]

    for x, label, color, y, size in markers:
        ax.plot(x, 0, marker='v', markersize=size, color=color, zorder=5)
        ax.plot([x, x], [0.3, y - 0.3], color=color, linewidth=2, linestyle='-', zorder=4)
        ax.text(x, y, label, ha='center', va='bottom', fontsize=11,
                fontweight='bold', color=color)

    # Gap zones
    # Gap 1: Phase 1 → EverMemOS (1.56pp)
    ax.fill_between([91.21, 92.77], -1.2, -0.7, color=C['danger'], alpha=0.2, zorder=1)
    ax.text(92.0, -1.5, '1.56pp gap', ha='center', fontsize=10, fontweight='bold',
            color=C['danger'])

    # Gap 2: EverMemOS → Target (3.23pp opportunity)
    ax.fill_between([92.77, 96.0], -1.2, -0.7, color=C['target'], alpha=0.15, zorder=1)
    ax.text(94.4, -1.5, '3.23pp opportunity zone', ha='center', fontsize=10,
            fontweight='bold', color=C['target'])

    ax.set_title('The Playing Field: Where We Stand vs. Where We\'re Going',
                fontsize=15, fontweight='bold', pad=15, color=C['text'])

    # Subtitle
    fig.text(0.5, 0.02, 'Every 1pp = ~15 more correct answers out of 1,540 questions',
            ha='center', fontsize=11, style='italic', color=C['dark'])

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_02_the_gap.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [2/12] The gap")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 3: Category Breakdown — Head-to-Head
# ═══════════════════════════════════════════════════════════════════════════

def chart_03_category_comparison():
    """Grouped bar: 4 categories, 4 systems side by side."""
    fig, ax = plt.subplots(figsize=(14, 7))

    categories = ['Cat 1\nSingle-Hop\n(282 questions)', 'Cat 2\nMulti-Hop\n(321 questions)',
                  'Cat 3\nTemporal\n(96 questions)', 'Cat 4\nOpen-Domain\n(841 questions)']

    # Measured data
    v3_scores     = [86.17, 85.67, 69.79, 90.37]    # v3 first run
    evermemos     = [91.10, 89.40, 78.10, 96.20]
    fc_scores     = [93.03, 91.90, 78.82, 96.51]

    x = np.arange(len(categories))
    width = 0.22

    b1 = ax.bar(x - width, v3_scores, width, label='Neuromem v3 (87.71%)',
                color=C['neuromem'], edgecolor='white', linewidth=2, alpha=0.85)
    b2 = ax.bar(x, evermemos, width, label='EverMemOS (92.77%)',
                color=C['evermemos'], edgecolor='white', linewidth=2, alpha=0.85)
    b3 = ax.bar(x + width, fc_scores, width, label='Full Context Ceiling (93.81%)',
                color=C['ceiling'], edgecolor='white', linewidth=2, alpha=0.85)

    # Labels
    for bars, scores in [(b1, v3_scores), (b2, evermemos), (b3, fc_scores)]:
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, score + 0.5,
                    f'{score:.1f}', ha='center', fontsize=8, fontweight='bold',
                    color=C['text'])

    # Highlight temporal gap
    rect = plt.Rectangle((1.7, 65), 0.6, 18, linewidth=2,
                          edgecolor=C['danger'], facecolor=C['danger'],
                          alpha=0.05, linestyle='--', zorder=1)
    ax.add_patch(rect)
    ax.text(2.0, 64, 'BIGGEST\nOPPORTUNITY', ha='center', fontsize=9,
            fontweight='bold', color=C['danger'])

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylabel('Accuracy (%)', fontsize=13, fontweight='bold')
    ax.set_ylim(60, 102)
    ax.set_title('Category Breakdown: Where Neuromem Wins and Loses',
                fontsize=15, fontweight='bold', pad=15)
    ax.legend(fontsize=11, loc='upper left')

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_03_category_comparison.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [3/12] Category comparison")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 4: Failure Taxonomy — What Goes Wrong
# ═══════════════════════════════════════════════════════════════════════════

def chart_04_failure_taxonomy():
    """Donut chart: 6 failure types from v3 analysis (357 failures)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

    # v3 failure data (357 failures where Neuromem wrong, EverMemOS right)
    labels = ['Retrieval\nMiss', 'Temporal\nConfusion', 'Multi-Hop\nChain Break',
              'Insufficient\nDetail', 'Wrong\nInference', 'Vocabulary\nMismatch']
    counts = [107, 89, 68, 57, 25, 11]
    colors = [C['danger'], C['evermemos'], C['amber'], C['neuromem'],
              C['dark'], C['light_purple']]

    # Donut chart
    wedges, texts, autotexts = ax1.pie(
        counts, labels=labels, colors=colors,
        autopct=lambda pct: f'{pct:.0f}%\n({int(round(pct/100*357))})',
        pctdistance=0.75, startangle=140,
        textprops={'fontsize': 9, 'fontweight': 'bold', 'color': C['text']},
        wedgeprops={'linewidth': 3, 'edgecolor': 'white'}
    )
    for autotext in autotexts:
        autotext.set_fontsize(8)

    centre_circle = plt.Circle((0, 0), 0.5, fc=C['bg'])
    ax1.add_artist(centre_circle)
    ax1.text(0, 0.08, '357', fontsize=28, fontweight='bold', ha='center',
             va='center', color=C['text'])
    ax1.text(0, -0.12, 'failures', fontsize=11, ha='center', va='center',
             color=C['dark'])
    ax1.set_title('What Goes Wrong\n(v3 at 87.71%)', fontsize=13,
                  fontweight='bold', pad=15)

    # Recovery potential bar chart
    failure_types = ['Retrieval\nMiss', 'Temporal', 'Multi-Hop', 'Insuff.\nDetail',
                     'Wrong\nInference', 'Vocab\nMismatch']
    counts_rev = [107, 89, 68, 57, 25, 11]
    recoverable = [85, 50, 45, 35, 5, 8]  # estimated with proposed improvements
    hard = [c - r for c, r in zip(counts_rev, recoverable)]

    y = np.arange(len(failure_types))
    ax2.barh(y, recoverable, color=C['target'], edgecolor='white', linewidth=2,
             height=0.6, alpha=0.85, label='Recoverable with proposed fixes')
    ax2.barh(y, hard, left=recoverable, color=C['danger'], edgecolor='white',
             linewidth=2, height=0.6, alpha=0.4, label='Irreducible / very hard')

    # Labels
    for i, (rec, tot) in enumerate(zip(recoverable, counts_rev)):
        ax2.text(tot + 2, i, f'{rec}/{tot}', va='center', fontsize=10,
                fontweight='bold', color=C['text'])

    ax2.set_yticks(y)
    ax2.set_yticklabels(failure_types, fontsize=10)
    ax2.set_xlabel('Number of Questions', fontsize=12)
    ax2.set_title('Recovery Potential\n(estimated)', fontsize=13,
                  fontweight='bold', pad=15)
    ax2.legend(fontsize=9, loc='lower right')

    fig.suptitle('Failure Analysis: Understanding What Goes Wrong to Fix It',
                fontsize=15, fontweight='bold', y=1.02)

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_04_failure_taxonomy.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [4/12] Failure taxonomy")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 5: Diminishing Returns — Model Size vs Gain
# ═══════════════════════════════════════════════════════════════════════════

def chart_05_diminishing_returns():
    """Scatter/line: model parameter increases vs accuracy gains."""
    fig, ax = plt.subplots(figsize=(12, 7))

    # Interventions plotted by "effort" vs "gain"
    interventions = [
        ('Structured\nPrompt', 1, 15.37, C['target'], 200),        # v2→v3 prompt change
        ('top_k\n15→100', 1, 8.0, C['target'], 180),               # within v3
        ('Modality\nReranking', 2, 2.0, C['target'], 160),         # within v3
        ('Reranker\n22M→435M', 20, 3.10, C['neuromem'], 300),      # Phase 0
        ('Embeddings\n8M→600M', 75, 0.40, C['amber'], 300),        # Phase 1
    ]

    for label, size_mult, gain, color, marker_size in interventions:
        ax.scatter(size_mult, gain, s=marker_size, c=color, edgecolors='white',
                   linewidth=2, zorder=5, alpha=0.9)
        # Label offset
        offset_x = 1.5 if size_mult < 30 else -8
        offset_y = 0.3
        ax.annotate(label, (size_mult, gain),
                    xytext=(offset_x, offset_y), textcoords='offset points',
                    fontsize=9, fontweight='bold', color=color,
                    ha='left' if size_mult < 30 else 'right')

    # Trend line showing diminishing returns
    x_trend = np.linspace(0.5, 100, 100)
    y_trend = 15.0 / (1 + 0.3 * x_trend)
    ax.plot(x_trend, y_trend, '--', color=C['danger'], alpha=0.4, linewidth=2,
            label='Diminishing returns curve')

    # Zone labels
    ax.fill_between([0.5, 5], 0, 20, alpha=0.05, color=C['target'])
    ax.fill_between([5, 100], 0, 20, alpha=0.05, color=C['danger'])
    ax.text(2, 18, 'HIGH LEVERAGE\n(Algorithmic changes)', fontsize=10,
            ha='center', color=C['target'], fontweight='bold', alpha=0.7)
    ax.text(40, 18, 'LOW LEVERAGE\n(Bigger models)', fontsize=10,
            ha='center', color=C['danger'], fontweight='bold', alpha=0.7)

    ax.set_xlabel('Relative Complexity / Model Size Increase (x)', fontsize=12,
                  fontweight='bold')
    ax.set_ylabel('Accuracy Gain (percentage points)', fontsize=12, fontweight='bold')
    ax.set_xscale('log')
    ax.set_xlim(0.5, 120)
    ax.set_ylim(-0.5, 20)
    ax.set_title('Diminishing Returns: Why Bigger Models Aren\'t the Answer Anymore',
                fontsize=15, fontweight='bold', pad=15)
    ax.legend(fontsize=10, loc='upper right')

    # Insight
    fig.text(0.5, -0.01,
            'The first 15pp came from a prompt change (free). The last 0.4pp cost a 75x model increase. The next gains must come from algorithms, not parameters.',
            ha='center', fontsize=10, style='italic', color=C['dark'])

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_05_diminishing_returns.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [5/12] Diminishing returns")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 6: Competitive Landscape — Horizontal Bar
# ═══════════════════════════════════════════════════════════════════════════

def chart_06_competitive_landscape():
    """Horizontal bar: all systems ranked by LoCoMo score."""
    fig, ax = plt.subplots(figsize=(14, 8))

    systems = [
        ('No Retrieval', 5.67, '#bdc3c7'),
        ('LangMem', 58.10, '#bdc3c7'),
        ('Mem0 (\\$24M)', 66.90, '#bdc3c7'),
        ('Neuromem v2', 72.34, C['light_blue']),
        ('Letta/MemGPT', 74.00, '#bdc3c7'),
        ('Zep/Graphiti', 75.10, '#bdc3c7'),
        ('SuperMemory', 81.60, '#bdc3c7'),
        ('Neuromem v3', 87.71, C['neuromem']),
        ('Hindsight', 91.40, '#bdc3c7'),
        ('Phase 0+1', 91.21, C['neuromem']),
        ('EverMemOS', 92.77, C['evermemos']),
        ('Neuromem FC', 93.81, C['ceiling']),
    ]

    names = [s[0] for s in systems]
    scores = [s[1] for s in systems]
    colors = [s[2] for s in systems]

    y = np.arange(len(systems))
    bars = ax.barh(y, scores, color=colors, edgecolor='white', linewidth=2,
                   height=0.65, alpha=0.85, zorder=3)

    # Score labels
    for i, (bar, score, name) in enumerate(zip(bars, scores, names)):
        offset = 1.5 if score < 85 else -6
        ha = 'left' if score < 85 else 'right'
        text_color = C['text'] if score < 85 else 'white'
        ax.text(score + offset, i, f'{score:.1f}%', va='center',
                fontsize=10, fontweight='bold', color=text_color, ha=ha)

    # Funding annotations
    funded = {
        'Mem0 (\\$24M)': '\\$24M raised',
        'Zep/Graphiti': 'Series A',
        'SuperMemory': '\\$2.6M raised',
        'Letta/MemGPT': 'Series A',
    }
    for name, funding in funded.items():
        idx = names.index(name)
        ax.text(2, idx, funding, va='center', fontsize=8, color=C['dark'],
                style='italic')

    # EverMemOS reference line
    ax.axvline(x=92.77, color=C['evermemos'], linestyle='--', alpha=0.4,
               linewidth=1.5, zorder=1)
    ax.text(93, len(systems) - 0.5, 'EverMemOS\n92.77%', fontsize=9,
            color=C['evermemos'], fontweight='bold')

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=10)
    ax.set_xlabel('LoCoMo Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_xlim(0, 100)
    ax.set_title('Competitive Landscape: Where Everyone Stands',
                fontsize=15, fontweight='bold', pad=15)

    # Insight
    fig.text(0.5, -0.01,
            'Neuromem already beats every funded competitor. The remaining target is EverMemOS — and exceeding it.',
            ha='center', fontsize=10, style='italic', color=C['dark'])

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_06_competitive_landscape.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [6/12] Competitive landscape")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 7: Cost vs Accuracy — The Efficiency Story
# ═══════════════════════════════════════════════════════════════════════════

def chart_07_cost_vs_accuracy():
    """Scatter: monthly cost vs accuracy for multiple systems."""
    fig, ax = plt.subplots(figsize=(12, 7))

    # (name, accuracy, monthly_cost, color, size)
    systems = [
        ('Neuromem v3\n(current)', 87.71, 12, C['neuromem'], 250),
        ('Neuromem Phase 1', 91.21, 14, C['neuromem'], 300),
        ('EverMemOS', 92.77, 207, C['evermemos'], 300),
        ('Mem0 Pro', 66.90, 249, '#bdc3c7', 150),
        ('SuperMemory', 81.60, 99, '#bdc3c7', 150),
        ('Zep Cloud', 75.10, 149, '#bdc3c7', 150),
        ('Neuromem Target\n(projected)', 96.0, 16, C['target'], 350),
    ]

    for name, acc, cost, color, size in systems:
        ax.scatter(cost, acc, s=size, c=color, edgecolors='white', linewidth=2,
                   zorder=5, alpha=0.9)
        # Label positioning
        offset_x = 15
        offset_y = 0
        ha = 'left'
        if cost > 200:
            offset_x = -15
            ha = 'right'
        ax.annotate(name, (cost, acc),
                    xytext=(offset_x, offset_y), textcoords='offset points',
                    fontsize=9, fontweight='bold', color=color, ha=ha, va='center')

    # Draw the "efficiency frontier"
    ax.fill_between([0, 20], 85, 100, alpha=0.05, color=C['target'])
    ax.text(10, 99, 'IDEAL ZONE\n(High accuracy,\nlow cost)', fontsize=10,
            ha='center', color=C['target'], fontweight='bold', alpha=0.5)

    ax.set_xlabel('Monthly Cost ($)', fontsize=12, fontweight='bold')
    ax.set_ylabel('LoCoMo Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_xlim(-10, 300)
    ax.set_ylim(60, 100)
    ax.set_title('The Efficiency Story: Accuracy Per Dollar',
                fontsize=15, fontweight='bold', pad=15)

    # Insight
    fig.text(0.5, -0.01,
            'EverMemOS costs \\$207/month for 92.77%. Neuromem targets 96%+ for \\$16/month — 13x cheaper.',
            ha='center', fontsize=10, style='italic', color=C['dark'])

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_07_cost_vs_accuracy.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [7/12] Cost vs accuracy")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 8: EverMemOS Weaknesses — Their Blind Spots
# ═══════════════════════════════════════════════════════════════════════════

def chart_08_evermemos_weaknesses():
    """Radar/comparison showing EverMemOS structural weaknesses."""
    fig, ax = plt.subplots(figsize=(12, 7))

    features = [
        'Temporal\nEngine',
        'Entity\nModeling',
        'Salience\nGuard',
        'Consolidation\n(Memory Decay)',
        'Local-First\n(Privacy)',
        'Cost\nEfficiency',
        'Extraction\nDepth',
        'Agentic\nRetrieval',
    ]

    # Capability scores (0-10) — honest assessment
    neuromem_scores = [6, 7, 8, 9, 10, 10, 3, 7]
    evermemos_scores = [4, 3, 0, 0, 2, 2, 10, 9]

    x = np.arange(len(features))
    width = 0.35

    b1 = ax.bar(x - width/2, neuromem_scores, width, label='Neuromem',
                color=C['neuromem'], edgecolor='white', linewidth=2, alpha=0.85)
    b2 = ax.bar(x + width/2, evermemos_scores, width, label='EverMemOS',
                color=C['evermemos'], edgecolor='white', linewidth=2, alpha=0.85)

    # Score labels
    for bars in [b1, b2]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h + 0.2,
                        f'{int(h)}', ha='center', fontsize=9, fontweight='bold',
                        color=C['text'])

    # Highlight Neuromem advantages
    for i, (n, e) in enumerate(zip(neuromem_scores, evermemos_scores)):
        if n > e + 2:
            ax.scatter(i - width/2, n + 0.8, marker='*', s=200, color=C['target'],
                      zorder=5, edgecolors='white', linewidth=1)

    ax.set_xticks(x)
    ax.set_xticklabels(features, fontsize=9)
    ax.set_ylabel('Capability Score (0-10)', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 12)
    ax.set_title('Feature Comparison: Neuromem\'s Advantages vs. EverMemOS',
                fontsize=15, fontweight='bold', pad=15)
    ax.legend(fontsize=11, loc='upper right')

    # Note
    fig.text(0.5, -0.01,
            '* = Neuromem significantly leads. EverMemOS has zero salience filtering, zero consolidation, and costs 13x more.',
            ha='center', fontsize=10, style='italic', color=C['dark'])

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_08_evermemos_weaknesses.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [8/12] EverMemOS weaknesses")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 9: Where The Points Come From — Stacked Recovery
# ═══════════════════════════════════════════════════════════════════════════

def chart_09_point_sources():
    """Stacked bar: projected point gains from each strategy."""
    fig, ax = plt.subplots(figsize=(14, 7))

    strategies = [
        'Category-Specific\nPipelines',
        'Multi-Step\nReasoning Chains',
        'Pre-Computed\nKnowledge\nStructures',
        'Temporal\nReasoning\nEngine',
        'Judge-Aware\nAnswer\nOptimization',
    ]

    # Conservative and optimistic gain estimates (percentage points)
    conservative = [1.5, 1.0, 1.0, 1.5, 0.5]
    optimistic = [2.5, 2.0, 2.0, 3.0, 1.5]
    extra = [o - c for o, c in zip(optimistic, conservative)]

    x = np.arange(len(strategies))

    b1 = ax.bar(x, conservative, color=C['neuromem'], edgecolor='white',
                linewidth=2, width=0.55, alpha=0.85, label='Conservative estimate')
    b2 = ax.bar(x, extra, bottom=conservative, color=C['light_blue'], edgecolor='white',
                linewidth=2, width=0.55, alpha=0.5, label='Optimistic upside')

    # Labels
    for i, (c, o) in enumerate(zip(conservative, optimistic)):
        ax.text(i, o + 0.15, f'+{c:.1f}–{o:.1f}pp', ha='center', fontsize=10,
                fontweight='bold', color=C['text'])

    ax.set_xticks(x)
    ax.set_xticklabels(strategies, fontsize=10)
    ax.set_ylabel('Projected Accuracy Gain (pp)', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 4)
    ax.set_title('Where the Next Points Come From: 5 Breakthrough Strategies',
                fontsize=15, fontweight='bold', pad=15)
    ax.legend(fontsize=11)

    # Summary
    total_c = sum(conservative)
    total_o = sum(optimistic)
    summary = f"Total projected gain: +{total_c:.1f}pp (conservative) to +{total_o:.1f}pp (optimistic)\n"
    summary += f"From 91.21% → {91.21 + total_c:.1f}%–{91.21 + total_o:.1f}%"
    ax.text(0.98, 0.95, summary, transform=ax.transAxes, fontsize=11,
            ha='right', va='top', fontweight='bold', color=C['dark'],
            bbox=dict(boxstyle='round,pad=0.5', facecolor=C['target'], alpha=0.1))

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_09_point_sources.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [9/12] Point sources")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 10: Temporal Deep Dive — The Biggest Weakness
# ═══════════════════════════════════════════════════════════════════════════

def chart_10_temporal_deep_dive():
    """Bar chart: temporal category performance across systems + breakdown."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Temporal scores across systems
    systems = ['Neuromem\nv2', 'Neuromem\nv3', 'Phase 0+1\n(current)',
               'EverMemOS', 'Full\nContext']
    temporal = [52.1, 69.79, 73.0, 78.10, 78.82]  # Phase 0+1 est ~73% based on recovery rates
    colors = [C['light_blue'], C['neuromem'], C['neuromem'],
              C['evermemos'], C['ceiling']]

    bars = ax1.bar(range(len(systems)), temporal, color=colors, edgecolor='white',
                   linewidth=2, width=0.55, alpha=0.85)

    for i, (bar, score) in enumerate(zip(bars, temporal)):
        label = f'{score:.1f}%'
        if i == 2:
            label += ' (est.)'
        ax1.text(i, score + 1, label, ha='center', fontsize=10, fontweight='bold',
                color=C['text'])

    ax1.set_xticks(range(len(systems)))
    ax1.set_xticklabels(systems, fontsize=9)
    ax1.set_ylabel('Cat 3 Temporal Accuracy (%)', fontsize=11, fontweight='bold')
    ax1.set_ylim(40, 90)
    ax1.set_title('Temporal Reasoning:\nThe Hardest Category', fontsize=13,
                  fontweight='bold', pad=10)

    # Right: Types of temporal failures
    temp_types = ['Sequence\nOrdering', 'Duration/\nFrequency', 'Boundary\nDetection',
                  'Relative\nTime', 'Event\nCounting']
    temp_counts = [25, 20, 18, 15, 11]
    temp_colors = [C['danger'], C['evermemos'], C['amber'], C['neuromem'], C['dark']]

    bars2 = ax2.barh(range(len(temp_types)), temp_counts, color=temp_colors,
                     edgecolor='white', linewidth=2, height=0.55, alpha=0.85)

    for i, (bar, count) in enumerate(zip(bars2, temp_counts)):
        ax2.text(count + 1, i, f'{count} failures', va='center', fontsize=10,
                fontweight='bold', color=C['text'])

    ax2.set_yticks(range(len(temp_types)))
    ax2.set_yticklabels(temp_types, fontsize=10)
    ax2.set_xlabel('Failure Count', fontsize=11, fontweight='bold')
    ax2.set_title('Types of Temporal Failures\n(89 total from v3)', fontsize=13,
                  fontweight='bold', pad=10)

    fig.suptitle('Temporal Reasoning: Where 8+ Points Are Hiding',
                fontsize=15, fontweight='bold', y=1.02)

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_10_temporal_deep_dive.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [10/12] Temporal deep dive")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 11: Implementation Roadmap
# ═══════════════════════════════════════════════════════════════════════════

def chart_11_implementation_roadmap():
    """Gantt-style: 3 horizons with time estimates and expected impact."""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Horizons and tasks
    tasks = [
        # (name, horizon, start_day, duration_days, color, expected_gain)
        ('LLM sufficiency check', 'H1', 0, 2, C['target'], '+0.5pp'),
        ('Multi-query Round 1', 'H1', 1, 2, C['target'], '+0.5pp'),
        ('Temporal extraction pass', 'H1', 2, 3, C['target'], '+1.0pp'),
        ('MaxSim-style scoring', 'H1', 3, 2, C['target'], '+0.5pp'),
        ('Benchmark Phase 0+1 config', 'H1', 5, 1, C['target'], 'verify'),
        ('Category-specific pipelines', 'H2', 7, 5, C['neuromem'], '+1.5pp'),
        ('Multi-step reasoning chains', 'H2', 9, 5, C['neuromem'], '+1.0pp'),
        ('Pre-computed knowledge graphs', 'H2', 11, 6, C['neuromem'], '+1.0pp'),
        ('Temporal reasoning engine', 'H2', 13, 5, C['neuromem'], '+1.5pp'),
        ('Judge-aware optimization', 'H2', 16, 3, C['neuromem'], '+0.5pp'),
        ('Full benchmark (1540q)', 'H3', 19, 2, C['ceiling'], 'validate'),
        ('Ablation studies', 'H3', 21, 3, C['ceiling'], 'analyze'),
        ('Documentation + paper', 'H3', 23, 4, C['ceiling'], 'publish'),
    ]

    for i, (name, horizon, start, dur, color, gain) in enumerate(tasks):
        ax.barh(i, dur, left=start, color=color, edgecolor='white',
                linewidth=2, height=0.6, alpha=0.85)
        # Task name (left)
        ax.text(start - 0.3, i, name, ha='right', va='center', fontsize=9,
                fontweight='bold', color=C['text'])
        # Gain (right)
        ax.text(start + dur + 0.3, i, gain, ha='left', va='center', fontsize=9,
                color=color, fontweight='bold')

    # Horizon dividers
    ax.axhline(y=4.5, color=C['grid'], linewidth=1, linestyle='-')
    ax.axhline(y=9.5, color=C['grid'], linewidth=1, linestyle='-')
    ax.text(-9, 2, 'H1: Foundation\n(~10 hours)', fontsize=11, fontweight='bold',
            color=C['target'], ha='center', va='center')
    ax.text(-9, 7, 'H2: Breakthroughs\n(~25 hours)', fontsize=11, fontweight='bold',
            color=C['neuromem'], ha='center', va='center')
    ax.text(-9, 11, 'H3: Validation\n(~10 hours)', fontsize=11, fontweight='bold',
            color=C['ceiling'], ha='center', va='center')

    ax.set_xlabel('Days from Start', fontsize=12, fontweight='bold')
    ax.set_xlim(-13, 30)
    ax.set_ylim(-0.5, len(tasks) - 0.5)
    ax.invert_yaxis()
    ax.set_yticks([])
    ax.set_title('Implementation Roadmap: Three Horizons to 96%+',
                fontsize=15, fontweight='bold', pad=15)

    # Milestone markers
    ax.axvline(x=6, color=C['target'], linestyle=':', alpha=0.5, linewidth=2)
    ax.text(6, len(tasks) - 0.3, '→93-94%', fontsize=10, color=C['target'],
            fontweight='bold', ha='center')
    ax.axvline(x=19, color=C['neuromem'], linestyle=':', alpha=0.5, linewidth=2)
    ax.text(19, len(tasks) - 0.3, '→96%+', fontsize=10, color=C['neuromem'],
            fontweight='bold', ha='center')

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_11_implementation_roadmap.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [11/12] Implementation roadmap")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 12: The Big Picture — Probability Distribution
# ═══════════════════════════════════════════════════════════════════════════

def chart_12_probability_distribution():
    """Bell curve showing probability distribution of final outcomes."""
    fig, ax = plt.subplots(figsize=(14, 7))

    # Normal distribution centered on expected outcome
    mean = 95.0
    std = 1.8
    x = np.linspace(88, 100, 500)
    y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)

    # Fill under curve
    ax.fill_between(x, y, alpha=0.15, color=C['neuromem'])
    ax.plot(x, y, color=C['neuromem'], linewidth=3, label='Projected outcome distribution')

    # Confidence intervals
    # 68% interval
    mask_68 = (x >= mean - std) & (x <= mean + std)
    ax.fill_between(x[mask_68], y[mask_68], alpha=0.2, color=C['neuromem'])
    ax.text(mean, max(y) * 0.5, '68% confidence\n93.2%–96.8%', ha='center',
            fontsize=10, color=C['neuromem'], fontweight='bold')

    # Key reference lines
    refs = [
        (91.21, 'Current\n(91.21%)', C['amber'], '--'),
        (92.77, 'EverMemOS\n(92.77%)', C['evermemos'], '--'),
        (93.81, 'FC Ceiling\n(93.81%)', C['ceiling'], ':'),
    ]

    for x_ref, label, color, style in refs:
        y_at_ref = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_ref - mean) / std) ** 2)
        ax.axvline(x=x_ref, color=color, linestyle=style, linewidth=2, alpha=0.6)
        ax.text(x_ref, max(y) * 1.05, label, ha='center', fontsize=9,
                fontweight='bold', color=color)

    # "Beat EverMemOS" probability
    from scipy import stats
    prob_beat_ever = 1 - stats.norm.cdf(92.77, mean, std)
    prob_beat_ceiling = 1 - stats.norm.cdf(93.81, mean, std)
    prob_95_plus = 1 - stats.norm.cdf(95.0, mean, std)

    prob_text = (
        f"P(beat EverMemOS) = {prob_beat_ever*100:.0f}%\n"
        f"P(beat FC ceiling) = {prob_beat_ceiling*100:.0f}%\n"
        f"P(reach 95%+) = {prob_95_plus*100:.0f}%"
    )
    ax.text(0.02, 0.95, prob_text, transform=ax.transAxes, fontsize=12,
            fontweight='bold', va='top', color=C['dark'],
            bbox=dict(boxstyle='round,pad=0.5', facecolor=C['target'], alpha=0.1))

    ax.set_xlabel('Final LoCoMo Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Probability Density', fontsize=12, fontweight='bold')
    ax.set_xlim(88, 100)
    ax.set_ylim(0, max(y) * 1.3)
    ax.set_title('Projected Final Accuracy Distribution (with all improvements)',
                fontsize=15, fontweight='bold', pad=15)
    ax.legend(fontsize=11)

    # Remove y-axis numbers (probability density isn't meaningful to reader)
    ax.set_yticklabels([])

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'deep_12_probability_distribution.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  [12/12] Probability distribution")


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print(f"Generating deep analysis charts in {CHARTS_DIR}/")
    print()

    chart_01_score_progression()
    chart_02_the_gap()
    chart_03_category_comparison()
    chart_04_failure_taxonomy()
    chart_05_diminishing_returns()
    chart_06_competitive_landscape()
    chart_07_cost_vs_accuracy()
    chart_08_evermemos_weaknesses()
    chart_09_point_sources()
    chart_10_temporal_deep_dive()
    chart_11_implementation_roadmap()
    chart_12_probability_distribution()

    print()
    print("Done! All 12 charts generated.")
    print(f"Charts directory: {CHARTS_DIR}")
