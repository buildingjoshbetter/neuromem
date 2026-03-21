#!/usr/bin/env python3
"""
Generate architecture upgrade analysis charts for Neuromem.
Produces ~10 PNGs visualizing the triple model upgrade impact.

Charts use ADHD-friendly design: high contrast, clear labels, minimal clutter.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import os

CHARTS_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Color palette ──────────────────────────────────────────────────────────
C = {
    'unchanged':  '#2ecc71',   # Green — unchanged/current
    'modified':   '#f39c12',   # Amber — modified modules
    'new_dep':    '#e74c3c',   # Red — new dependency
    'current':    '#3498db',   # Blue — current state
    'upgraded':   '#9b59b6',   # Purple — upgraded state
    'evermemos':  '#e67e22',   # Orange — EverMemOS reference
    'bg':         '#faf9f6',   # Cream background
    'grid':       '#e0e0e0',
    'text':       '#2c3e50',
    'light_blue': '#85c1e9',
    'light_purple':'#c39bd3',
    'green_ok':   '#27ae60',
    'yellow_warn':'#f1c40f',
    'red_fail':   '#e74c3c',
    'dark':       '#34495e',
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
})


# ═══════════════════════════════════════════════════════════════════════════
# Chart 1: Pipeline Comparison — Current vs Upgraded
# ═══════════════════════════════════════════════════════════════════════════

def chart_01_pipeline_comparison():
    """Dual flow diagram: current vs upgraded pipeline."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))

    # Current pipeline steps
    current_steps = [
        ("Query Input", C['unchanged']),
        ("Query Classifier", C['unchanged']),
        ("FTS5 Keyword\nSearch (BM25)", C['unchanged']),
        ("Model2Vec 8M\nVector Search", C['modified']),
        ("RRF Hybrid\nFusion", C['unchanged']),
        ("MiniLM Reranker\n(22M params)", C['modified']),
        ("Salience Guard +\nTemporal Filter", C['unchanged']),
        ("LLM Answer\n(API)", C['unchanged']),
    ]

    # Upgraded pipeline steps
    upgraded_steps = [
        ("Query Input", C['unchanged']),
        ("Query Classifier", C['unchanged']),
        ("FTS5 Keyword\nSearch (BM25)", C['unchanged']),
        ("Qwen3-0.6B\nVector Search", C['new_dep']),
        ("RRF Hybrid\nFusion", C['unchanged']),
        ("mxbai-rerank-large\n(435M params)", C['new_dep']),
        ("Salience Guard +\nTemporal Filter", C['unchanged']),
        ("LLM Answer\n(API)", C['unchanged']),
    ]

    for ax, steps, title in [(ax1, current_steps, "CURRENT Pipeline"),
                              (ax2, upgraded_steps, "UPGRADED Pipeline")]:
        ax.set_xlim(0, 10)
        ax.set_ylim(-0.5, len(steps) - 0.5)
        ax.invert_yaxis()
        ax.set_title(title, fontsize=14, fontweight='bold', color=C['text'], pad=15)
        ax.axis('off')

        for i, (label, color) in enumerate(steps):
            # Box
            rect = plt.Rectangle((1, i - 0.35), 8, 0.7, linewidth=2,
                                  edgecolor=color, facecolor=color, alpha=0.15,
                                  zorder=2)
            ax.add_patch(rect)
            # Border
            rect2 = plt.Rectangle((1, i - 0.35), 8, 0.7, linewidth=2,
                                   edgecolor=color, facecolor='none', zorder=3)
            ax.add_patch(rect2)
            # Text
            ax.text(5, i, label, ha='center', va='center', fontsize=10,
                    fontweight='bold', color=C['text'], zorder=4)
            # Arrow
            if i < len(steps) - 1:
                ax.annotate('', xy=(5, i + 0.45), xytext=(5, i + 0.55),
                           arrowprops=dict(arrowstyle='->', color=C['dark'],
                                          lw=1.5))

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=C['unchanged'], alpha=0.3, edgecolor=C['unchanged'], label='Unchanged'),
        mpatches.Patch(facecolor=C['modified'], alpha=0.3, edgecolor=C['modified'], label='Being replaced'),
        mpatches.Patch(facecolor=C['new_dep'], alpha=0.3, edgecolor=C['new_dep'], label='New model'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3,
              fontsize=11, frameon=True, fancybox=True)

    fig.suptitle('Search Pipeline: Before & After Upgrade',
                fontsize=16, fontweight='bold', color=C['text'], y=0.98)
    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    fig.savefig(os.path.join(CHARTS_DIR, 'arch_01_pipeline_comparison.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  [1/10] Pipeline comparison")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 2: Model Scale (log-scale bar)
# ═══════════════════════════════════════════════════════════════════════════

def chart_02_model_scale():
    """Log-scale bar chart: 8M → 22M → 600M → 435M → 8B params."""
    fig, ax = plt.subplots(figsize=(12, 6))

    models = [
        ('Model2Vec\npotion-8M\n(current embed)', 8, C['current']),
        ('MiniLM-L6\n(current reranker)', 22, C['current']),
        ('mxbai-rerank-large\n(new reranker)', 435, C['new_dep']),
        ('Qwen3-Embedding\n0.6B (new embed)', 600, C['new_dep']),
        ('Qwen3-Embedding\n8B (GPU tier)', 8000, C['dark']),
    ]

    names = [m[0] for m in models]
    params = [m[1] for m in models]
    colors = [m[2] for m in models]

    bars = ax.barh(range(len(models)), params, color=colors, edgecolor='white',
                   linewidth=2, height=0.6, alpha=0.85)

    ax.set_xscale('log')
    ax.set_xticks([1, 10, 100, 1000, 10000])
    ax.set_xticklabels(['1M', '10M', '100M', '1B', '10B'])
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(names, fontsize=10)
    ax.set_xlabel('Parameters (log scale)', fontsize=12, color=C['text'])

    # Value labels
    for i, (bar, p) in enumerate(zip(bars, params)):
        label = f"{p/1000:.1f}B" if p >= 1000 else f"{p}M"
        ax.text(p * 1.3, i, label, va='center', fontsize=11, fontweight='bold',
                color=C['text'])

    # Annotations
    ax.annotate('75x larger\nembeddings', xy=(600, 3), xytext=(100, 3.5),
               fontsize=9, color=C['new_dep'], fontweight='bold',
               arrowprops=dict(arrowstyle='->', color=C['new_dep']))
    ax.annotate('20x larger\nreranker', xy=(435, 2), xytext=(60, 1.3),
               fontsize=9, color=C['new_dep'], fontweight='bold',
               arrowprops=dict(arrowstyle='->', color=C['new_dep']))

    ax.set_title('Model Parameter Scale: Current → Upgraded',
                fontsize=14, fontweight='bold', color=C['text'])

    legend_elements = [
        mpatches.Patch(color=C['current'], label='Current models'),
        mpatches.Patch(color=C['new_dep'], label='Upgrade targets'),
        mpatches.Patch(color=C['dark'], label='GPU-only option'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'arch_02_model_scale.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  [2/10] Model scale")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 3: RAM Footprint (stacked bar)
# ═══════════════════════════════════════════════════════════════════════════

def chart_03_ram_footprint():
    """Stacked bar: Before/after RAM by component."""
    fig, ax = plt.subplots(figsize=(10, 6))

    categories = ['Current\n(MacBook)', 'Upgraded\n(MacBook)', 'Upgraded + GPU\n(8B embed on GPU)']

    # Components: [SQLite/FTS5, Embedding Model, Reranker, Python/Overhead]
    sqlite_fts = [20, 20, 20]           # MB
    embedding  = [15, 1500, 200]        # Model2Vec=15MB, Qwen3-0.6B=1500MB, on GPU=200MB overhead
    reranker   = [100, 600, 600]        # MiniLM=100MB, mxbai-large=600MB INT8
    overhead   = [50, 80, 80]           # Python process overhead

    x = np.arange(len(categories))
    width = 0.5

    b1 = ax.bar(x, sqlite_fts, width, label='SQLite + FTS5', color=C['unchanged'], edgecolor='white')
    b2 = ax.bar(x, embedding, width, bottom=sqlite_fts, label='Embedding Model', color=C['upgraded'], edgecolor='white')
    b3 = ax.bar(x, reranker, width,
                bottom=[s+e for s,e in zip(sqlite_fts, embedding)],
                label='Reranker', color=C['new_dep'], edgecolor='white')
    b4 = ax.bar(x, overhead, width,
                bottom=[s+e+r for s,e,r in zip(sqlite_fts, embedding, reranker)],
                label='Python Overhead', color=C['dark'], alpha=0.5, edgecolor='white')

    # Total labels
    totals = [s+e+r+o for s,e,r,o in zip(sqlite_fts, embedding, reranker, overhead)]
    for i, total in enumerate(totals):
        label = f"{total/1000:.1f} GB" if total >= 1000 else f"{total} MB"
        ax.text(i, total + 30, label, ha='center', fontsize=12, fontweight='bold',
                color=C['text'])

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylabel('RAM Usage (MB)', fontsize=12, color=C['text'])
    ax.set_title('Memory Footprint: Before & After Upgrade',
                fontsize=14, fontweight='bold', color=C['text'])
    ax.legend(loc='upper left', fontsize=10)

    # Reference line
    ax.axhline(y=8000, color=C['grid'], linestyle='--', alpha=0.5)
    ax.text(2.3, 8100, '8 GB MacBook limit', fontsize=9, color='gray', ha='right')

    ax.set_ylim(0, max(totals) * 1.25)
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'arch_03_ram_footprint.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  [3/10] RAM footprint")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 4: Query Latency Waterfall
# ═══════════════════════════════════════════════════════════════════════════

def chart_04_query_latency():
    """Horizontal waterfall: per-step timing before vs after."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

    steps = ['Query\nClassify', 'FTS5\nSearch', 'Vector\nSearch', 'RRF\nFusion',
             'Reranker', 'Salience\nFilter', 'LLM\nAnswer']

    # Current times (ms)
    current_ms = [2, 5, 3, 1, 80, 5, 2000]
    # Upgraded times (ms)
    upgraded_ms = [2, 5, 50, 1, 350, 5, 2000]

    colors_current = [C['unchanged']]*7
    colors_upgraded = [C['unchanged'], C['unchanged'], C['new_dep'], C['unchanged'],
                       C['new_dep'], C['unchanged'], C['unchanged']]

    # Current
    left = 0
    for i, (step, ms) in enumerate(zip(steps, current_ms)):
        ax1.barh(0, ms, left=left, color=colors_current[i], edgecolor='white',
                height=0.5, alpha=0.85)
        if ms > 15:
            ax1.text(left + ms/2, 0, f"{ms}ms", ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white')
        left += ms

    ax1.text(left + 50, 0, f"Total: {sum(current_ms)}ms", va='center',
            fontsize=11, fontweight='bold', color=C['text'])
    ax1.set_title('CURRENT: Query Latency Breakdown', fontsize=12,
                 fontweight='bold', color=C['text'])
    ax1.set_yticks([])

    # Upgraded
    left = 0
    for i, (step, ms) in enumerate(zip(steps, upgraded_ms)):
        ax2.barh(0, ms, left=left, color=colors_upgraded[i], edgecolor='white',
                height=0.5, alpha=0.85)
        if ms > 15:
            ax2.text(left + ms/2, 0, f"{ms}ms", ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white')
        left += ms

    ax2.text(left + 50, 0, f"Total: {sum(upgraded_ms)}ms", va='center',
            fontsize=11, fontweight='bold', color=C['text'])
    ax2.set_title('UPGRADED: Query Latency Breakdown', fontsize=12,
                 fontweight='bold', color=C['text'])
    ax2.set_yticks([])
    ax2.set_xlabel('Time (milliseconds)', fontsize=11, color=C['text'])

    # Step labels at bottom
    cumulative = 0
    for step, ms_c, ms_u in zip(steps, current_ms, upgraded_ms):
        mid = cumulative + max(ms_c, ms_u)/2
        ax2.text(cumulative + ms_u/2, -0.5, step, ha='center', va='top',
                fontsize=8, color=C['text'])
        cumulative += ms_u

    fig.suptitle('Per-Step Query Latency (single query)',
                fontsize=14, fontweight='bold', color=C['text'], y=1.01)

    # Key insight
    fig.text(0.5, -0.02, 'LLM answer dominates (2000ms). Embedding/reranker upgrade adds ~315ms — invisible to user.',
            ha='center', fontsize=10, style='italic', color=C['dark'])

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'arch_04_query_latency.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  [4/10] Query latency")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 5: Modules Changed (Donut)
# ═══════════════════════════════════════════════════════════════════════════

def chart_05_modules_changed():
    """Donut chart: 2 changed / 16 unchanged modules."""
    fig, ax = plt.subplots(figsize=(8, 8))

    # 18 total modules, 2 changed (vector_search.py, reranker.py)
    sizes = [2, 16]
    labels = ['Modified\n(2 modules)', 'Unchanged\n(16 modules)']
    colors = [C['new_dep'], C['unchanged']]
    explode = (0.05, 0)

    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.0f%%', pctdistance=0.75, startangle=90,
        textprops={'fontsize': 13, 'fontweight': 'bold', 'color': C['text']},
        wedgeprops={'linewidth': 3, 'edgecolor': 'white'}
    )
    for autotext in autotexts:
        autotext.set_fontsize(14)
        autotext.set_fontweight('bold')

    # Donut hole
    centre_circle = plt.Circle((0, 0), 0.55, fc=C['bg'])
    ax.add_artist(centre_circle)

    # Center text
    ax.text(0, 0.08, '18', fontsize=36, fontweight='bold', ha='center', va='center',
           color=C['text'])
    ax.text(0, -0.12, 'modules', fontsize=14, ha='center', va='center',
           color=C['dark'])

    # List the changed modules
    changed = "Changed:\n  vector_search.py\n  reranker.py"
    ax.text(-1.3, -1.1, changed, fontsize=10, fontfamily='monospace',
           color=C['new_dep'], fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor=C['new_dep'], alpha=0.1))

    ax.set_title('Code Impact: Only 2 of 18 Modules Change',
                fontsize=14, fontweight='bold', color=C['text'], pad=20)
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'arch_05_modules_changed.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  [5/10] Modules changed")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 6: Ingestion Time (Stacked Bar)
# ═══════════════════════════════════════════════════════════════════════════

def chart_06_ingestion_time():
    """Stacked bar: ingestion breakdown before/after at different scales."""
    fig, ax = plt.subplots(figsize=(12, 6))

    scales = ['5K messages', '50K messages', '100K messages', '500K messages']
    x = np.arange(len(scales))
    width = 0.35

    # Current (Model2Vec is insanely fast for embedding)
    # Components: [Load/Parse, FTS5 Index, Vector Embed, Build Profiles]
    current_load    = [0.5, 3, 6, 30]      # seconds
    current_fts     = [0.3, 2, 4, 20]
    current_embed   = [0.2, 2, 4, 20]      # Model2Vec: ~25K/s
    current_profile = [1, 5, 10, 50]

    # Upgraded (Qwen3-0.6B is ~20 sentences/sec on CPU)
    upgraded_load    = [0.5, 3, 6, 30]
    upgraded_fts     = [0.3, 2, 4, 20]
    upgraded_embed   = [250, 2500, 5000, 25000]  # ~20/s on CPU = 250s for 5K
    upgraded_profile = [1, 5, 10, 50]

    # Convert to minutes for readability
    def to_min(arr):
        return [v/60 for v in arr]

    c_total = [sum(x) for x in zip(current_load, current_fts, current_embed, current_profile)]
    u_total = [sum(x) for x in zip(upgraded_load, upgraded_fts, upgraded_embed, upgraded_profile)]

    bars1 = ax.bar(x - width/2, to_min(c_total), width, label='Current (Model2Vec)',
                   color=C['current'], edgecolor='white', alpha=0.85)
    bars2 = ax.bar(x + width/2, to_min(u_total), width, label='Upgraded (Qwen3-0.6B CPU)',
                   color=C['new_dep'], edgecolor='white', alpha=0.85)

    # Labels
    for i, (c, u) in enumerate(zip(c_total, u_total)):
        c_label = f"{c:.0f}s" if c < 60 else f"{c/60:.0f}min"
        u_label = f"{u/60:.0f}min" if u < 3600 else f"{u/3600:.1f}hr"
        ax.text(i - width/2, c/60 + 1, c_label, ha='center', fontsize=9,
                fontweight='bold', color=C['current'])
        ax.text(i + width/2, u/60 + 1, u_label, ha='center', fontsize=9,
                fontweight='bold', color=C['new_dep'])

    ax.set_xticks(x)
    ax.set_xticklabels(scales, fontsize=11)
    ax.set_ylabel('Ingestion Time (minutes)', fontsize=12, color=C['text'])
    ax.set_title('One-Time Re-Ingestion Cost When Switching Models',
                fontsize=14, fontweight='bold', color=C['text'])
    ax.legend(fontsize=11)

    # Tip
    fig.text(0.5, -0.02,
            'TIP: Run overnight. 100K messages = ~83 min with Qwen3-0.6B on CPU. Only happens once.',
            ha='center', fontsize=10, style='italic', color=C['dark'])

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'arch_06_ingestion_time.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  [6/10] Ingestion time")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 7: GPU Offline Behavior (Traffic Light Grid)
# ═══════════════════════════════════════════════════════════════════════════

def chart_07_gpu_offline():
    """Traffic-light grid: what works/degrades/fails when GPU box is offline."""
    fig, ax = plt.subplots(figsize=(12, 7))

    features = [
        'FTS5 Keyword Search',
        'Vector Search (Qwen3-0.6B)',
        'RRF Hybrid Fusion',
        'Reranker (mxbai-large)',
        'Salience Guard',
        'Temporal Reasoning',
        'Personality Profiles',
        'Consolidation',
        'HyDE Query Expansion',
        'Episode Extraction',
        'LLM Answer Generation',
    ]

    # Status for each scenario: 0=works, 1=degraded, 2=fails
    # Columns: MacBook only, MacBook+GPU, GPU offline fallback
    scenarios = ['All Local\n(MacBook)', 'MacBook +\nGPU Box', 'GPU Box\nOffline']

    # Grid data (feature x scenario)
    grid = np.array([
        [0, 0, 0],   # FTS5 — always local
        [1, 0, 1],   # Vector — slow on CPU, fast on GPU, degrades if GPU offline
        [0, 0, 0],   # RRF — always local
        [1, 0, 1],   # Reranker — slow on CPU, fast on GPU
        [0, 0, 0],   # Salience — always local
        [0, 0, 0],   # Temporal — always local
        [0, 0, 0],   # Personality — always local
        [0, 0, 0],   # Consolidation — always local
        [1, 0, 1],   # HyDE — needs LLM, degrades without GPU
        [1, 0, 1],   # Episode Extraction — needs LLM
        [0, 0, 0],   # LLM Answer — uses cloud API
    ])

    color_map = {0: C['green_ok'], 1: C['yellow_warn'], 2: C['red_fail']}
    label_map = {0: 'WORKS', 1: 'SLOWER', 2: 'FAILS'}

    ax.set_xlim(-0.5, len(scenarios) - 0.5)
    ax.set_ylim(-0.5, len(features) - 0.5)
    ax.invert_yaxis()

    for i, feature in enumerate(features):
        for j, scenario in enumerate(scenarios):
            status = grid[i, j]
            color = color_map[status]
            rect = plt.Rectangle((j - 0.45, i - 0.4), 0.9, 0.8,
                                  facecolor=color, alpha=0.3,
                                  edgecolor=color, linewidth=2)
            ax.add_patch(rect)
            ax.text(j, i, label_map[status], ha='center', va='center',
                   fontsize=9, fontweight='bold', color=color)

    ax.set_xticks(range(len(scenarios)))
    ax.set_xticklabels(scenarios, fontsize=11, fontweight='bold')
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(features, fontsize=10)
    ax.set_title('Graceful Degradation: What Happens When GPU Box Goes Offline?',
                fontsize=14, fontweight='bold', color=C['text'], pad=15)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=C['green_ok'], alpha=0.3, edgecolor=C['green_ok'],
                      linewidth=2, label='Works normally'),
        mpatches.Patch(facecolor=C['yellow_warn'], alpha=0.3, edgecolor=C['yellow_warn'],
                      linewidth=2, label='Works but slower (CPU fallback)'),
        mpatches.Patch(facecolor=C['red_fail'], alpha=0.3, edgecolor=C['red_fail'],
                      linewidth=2, label='Fails (needs external service)'),
    ]
    ax.legend(handles=legend_elements, loc='lower center',
             bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=10)

    ax.grid(False)
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'arch_07_gpu_offline.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  [7/10] GPU offline behavior")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 8: Database Size (Bar)
# ═══════════════════════════════════════════════════════════════════════════

def chart_08_db_size():
    """Bar chart: database size before vs after at various message counts."""
    fig, ax = plt.subplots(figsize=(10, 6))

    scales = ['10K\nmessages', '50K\nmessages', '100K\nmessages', '500K\nmessages']
    x = np.arange(len(scales))
    width = 0.3

    # Current: 256-dim vectors, ~1KB per vector + message text
    # 256 floats * 4 bytes = 1024 bytes per vector
    current_db = [15, 70, 140, 700]     # MB (messages + FTS + 256-dim vectors)

    # Upgraded: 1024-dim vectors = 4096 bytes per vector (4x larger vectors)
    upgraded_db = [25, 120, 240, 1200]  # MB

    bars1 = ax.bar(x - width/2, current_db, width, label='Current (256-dim)',
                   color=C['current'], edgecolor='white', alpha=0.85)
    bars2 = ax.bar(x + width/2, upgraded_db, width, label='Upgraded (1024-dim)',
                   color=C['upgraded'], edgecolor='white', alpha=0.85)

    # Labels
    for i, (c, u) in enumerate(zip(current_db, upgraded_db)):
        c_label = f"{c} MB" if c < 1000 else f"{c/1000:.1f} GB"
        u_label = f"{u} MB" if u < 1000 else f"{u/1000:.1f} GB"
        ax.text(i - width/2, c + 10, c_label, ha='center', fontsize=9,
                fontweight='bold', color=C['current'])
        ax.text(i + width/2, u + 10, u_label, ha='center', fontsize=9,
                fontweight='bold', color=C['upgraded'])

    ax.set_xticks(x)
    ax.set_xticklabels(scales, fontsize=11)
    ax.set_ylabel('Database File Size (MB)', fontsize=12, color=C['text'])
    ax.set_title('SQLite Database Size: 256-dim vs 1024-dim Vectors',
                fontsize=14, fontweight='bold', color=C['text'])
    ax.legend(fontsize=11, loc='upper left')

    # Context
    fig.text(0.5, -0.02,
            'Even at 500K messages, the database fits on a USB stick. Still a single file.',
            ha='center', fontsize=10, style='italic', color=C['dark'])

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'arch_08_db_size.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  [8/10] Database size")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 9: Accuracy Projection (Bar with Error Bars)
# ═══════════════════════════════════════════════════════════════════════════

def chart_09_accuracy_projection():
    """Bar chart with error bars: baseline → projected with each upgrade."""
    fig, ax = plt.subplots(figsize=(12, 6))

    configs = [
        'Neuromem v2\n(baseline)',
        'Neuromem v3\n(current)',
        '+ Reranker\nUpgrade',
        '+ Embedding\nUpgrade',
        '+ Both\nUpgrades',
        'EverMemOS\n(target)',
    ]

    scores = [72.34, 87.71, 90.5, 90.0, 93.5, 92.77]
    errors_low = [0, 0.33, 1.5, 2.0, 2.5, 0]
    errors_high = [0, 0.33, 1.5, 2.5, 3.0, 0]

    colors = [C['dark'], C['current'], C['upgraded'], C['upgraded'],
              C['new_dep'], C['evermemos']]

    x = np.arange(len(configs))
    bars = ax.bar(x, scores, color=colors, edgecolor='white', linewidth=2,
                  width=0.6, alpha=0.85)

    # Error bars for projections
    ax.errorbar(x, scores,
               yerr=[errors_low, errors_high],
               fmt='none', ecolor=C['text'], elinewidth=2, capsize=5, capthick=2)

    # Labels
    for i, (bar, score) in enumerate(zip(bars, scores)):
        label = f"{score:.1f}%"
        if i > 1 and i < 5:
            label += " (est.)"
        ax.text(i, score + max(errors_high[i], 0) + 0.5, label,
               ha='center', fontsize=10, fontweight='bold', color=C['text'])

    # EverMemOS reference line
    ax.axhline(y=92.77, color=C['evermemos'], linestyle='--', alpha=0.5, linewidth=1.5)
    ax.text(5.3, 93, 'EverMemOS', fontsize=9, color=C['evermemos'], fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(configs, fontsize=10)
    ax.set_ylabel('LoCoMo Accuracy (%)', fontsize=12, color=C['text'])
    ax.set_ylim(65, 100)
    ax.set_title('Projected Accuracy: Cumulative Upgrade Impact',
                fontsize=14, fontweight='bold', color=C['text'])

    # Arrow showing gap closed
    ax.annotate('', xy=(4, 93.5), xytext=(1, 87.71),
               arrowprops=dict(arrowstyle='->', color=C['unchanged'],
                              lw=2, connectionstyle='arc3,rad=0.2'))
    ax.text(2.5, 90, '+5.8pp\nprojected', fontsize=9, fontweight='bold',
           color=C['unchanged'], ha='center')

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'arch_09_accuracy_projection.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  [9/10] Accuracy projection")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 10: Where Things Run (Grouped Bar / Treemap-like)
# ═══════════════════════════════════════════════════════════════════════════

def chart_10_where_things_run():
    """Grouped bar: MacBook vs GPU box vs Cloud breakdown."""
    fig, ax = plt.subplots(figsize=(12, 7))

    components = [
        'SQLite DB',
        'FTS5 Search',
        'Embedding\n(Qwen3-0.6B)',
        'Reranker\n(mxbai-large)',
        'Salience Guard',
        'Temporal',
        'Personality',
        'Consolidation',
        'HyDE Generation',
        'Episode\nExtraction',
        'Answer LLM',
    ]

    # Where each runs: height represents "weight" of component
    # MacBook / GPU Box / Cloud API
    macbook = [1, 1, 0.5, 0.5, 1, 1, 1, 1, 0, 0, 0]
    gpu_box = [0, 0, 0.5, 0.5, 0, 0, 0, 0, 1, 1, 0]
    cloud   = [0, 0, 0,   0,   0, 0, 0, 0, 0, 0, 1]

    x = np.arange(len(components))
    width = 0.25

    bars1 = ax.bar(x - width, macbook, width, label='MacBook (local)',
                   color=C['current'], edgecolor='white', alpha=0.85)
    bars2 = ax.bar(x, gpu_box, width, label='GPU Box (192.168.1.182)',
                   color=C['upgraded'], edgecolor='white', alpha=0.85)
    bars3 = ax.bar(x + width, cloud, width, label='Cloud API (Anthropic/OpenAI)',
                   color=C['evermemos'], edgecolor='white', alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(components, fontsize=9, rotation=30, ha='right')
    ax.set_ylabel('Runs Here (1 = primary, 0.5 = shared)', fontsize=11, color=C['text'])
    ax.set_title('Where Each Component Runs After Upgrade',
                fontsize=14, fontweight='bold', color=C['text'])
    ax.legend(fontsize=11, loc='upper right')
    ax.set_ylim(0, 1.3)

    # Summary boxes
    summary_text = "8 of 11 components run entirely on MacBook\n2 can offload to GPU box\n1 requires cloud API"
    ax.text(0.02, 0.95, summary_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round,pad=0.5', facecolor=C['unchanged'], alpha=0.15))

    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'arch_10_where_things_run.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  [10/10] Where things run")


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print(f"Generating architecture charts in {CHARTS_DIR}/")
    print()

    chart_01_pipeline_comparison()
    chart_02_model_scale()
    chart_03_ram_footprint()
    chart_04_query_latency()
    chart_05_modules_changed()
    chart_06_ingestion_time()
    chart_07_gpu_offline()
    chart_08_db_size()
    chart_09_accuracy_projection()
    chart_10_where_things_run()

    print()
    print("Done! All 10 charts generated.")
