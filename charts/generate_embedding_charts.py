#!/usr/bin/env python3
"""Generate charts for the Embedding Model Guide."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

CHARTS_DIR = os.path.dirname(os.path.abspath(__file__))

# Color palette
COLORS = {
    'current': '#e74c3c',       # Red - current model
    'drop_in': '#e67e22',       # Orange - drop-in upgrades
    'small': '#2ecc71',         # Green - small models
    'medium': '#3498db',        # Blue - medium models
    'large': '#9b59b6',         # Purple - large models
    'gpu': '#34495e',           # Dark - GPU-only
    'bg': '#faf9f6',            # Cream background
    'grid': '#ddd',
    'text': '#2c3e50',
}

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.facecolor': COLORS['bg'],
    'figure.facecolor': COLORS['bg'],
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.color': COLORS['grid'],
})


def chart_25_quality_vs_params():
    """Chart 25: Retrieval quality vs model parameters (log scale)."""
    fig, ax = plt.subplots(figsize=(12, 7))

    models = [
        ('potion-base-8M\n(current)', 8, 32, COLORS['current'], 200),
        ('potion-retrieval-32M', 32, 36, COLORS['drop_in'], 150),
        ('mdbr-leaf-ir', 23, 54, COLORS['small'], 150),
        ('arctic-embed-s', 33, 52, COLORS['small'], 150),
        ('bge-small-en-v1.5', 33, 52, COLORS['small'], 150),
        ('nomic-v1.5', 137, 53, COLORS['medium'], 180),
        ('gte-modernbert', 149, 55, COLORS['medium'], 180),
        ('arctic-embed-m-v2', 109, 54, COLORS['medium'], 150),
        ('Qwen3-0.6B', 600, 62, COLORS['large'], 220),
        ('Qwen3-4B', 4000, 68, COLORS['gpu'], 200),
        ('Qwen3-8B', 8000, 69, COLORS['gpu'], 200),
    ]

    for name, params, score, color, size in models:
        ax.scatter(params, score, s=size, c=color, edgecolors='white',
                  linewidth=1.5, zorder=5)
        offset_x = 1.15
        offset_y = 0.8
        if 'current' in name:
            offset_y = -2
        elif 'leaf' in name:
            offset_y = 1.5
        elif 'bge' in name:
            offset_y = -2
        elif 'modernbert' in name:
            offset_y = 1.2
        elif 'nomic' in name:
            offset_y = -2
        elif 'arctic-embed-m' in name:
            offset_y = -2
            offset_x = 0.7
        ax.annotate(name, (params, score),
                   textcoords="offset points", xytext=(8, offset_y),
                   fontsize=8, color=COLORS['text'])

    ax.set_xscale('log')
    ax.set_xlabel('Parameters (millions)', fontsize=12, color=COLORS['text'])
    ax.set_ylabel('Retrieval Quality (nDCG@10)', fontsize=12, color=COLORS['text'])
    ax.set_title('Embedding Model Quality vs. Size', fontsize=14, fontweight='bold', color=COLORS['text'])

    # Add quality zones
    ax.axhspan(30, 40, alpha=0.05, color='red', label='Current (potion-base-8M)')
    ax.axhspan(50, 56, alpha=0.05, color='blue', label='Competitive retrieval')
    ax.axhspan(60, 70, alpha=0.05, color='green', label='State-of-the-art')

    ax.set_xlim(5, 12000)
    ax.set_ylim(28, 72)
    ax.legend(loc='lower right', fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, '25_quality_vs_params.png'), dpi=150)
    plt.close()
    print("Generated: 25_quality_vs_params.png")


def chart_26_latency_comparison():
    """Chart 26: Latency comparison across models."""
    fig, ax = plt.subplots(figsize=(12, 6))

    models = [
        'potion-base-8M\n(current)',
        'potion-retrieval\n-32M',
        'm2v-Qwen3\n(distilled)',
        'arctic-embed-s\n(ONNX int8)',
        'bge-small\n(ONNX int8)',
        'nomic-v1.5\n(GGUF)',
        'gte-modernbert\n(PyTorch)',
        'Qwen3-0.6B\n(PyTorch CPU)',
        'Qwen3-4B\n(GPU only)',
    ]

    # Latency per single query embedding (ms)
    latency = [0.04, 0.04, 0.04, 5, 5, 15, 20, 50, 10]

    colors = [
        COLORS['current'], COLORS['drop_in'], COLORS['drop_in'],
        COLORS['small'], COLORS['small'],
        COLORS['medium'], COLORS['medium'],
        COLORS['large'], COLORS['gpu'],
    ]

    bars = ax.bar(range(len(models)), latency, color=colors, edgecolor='white', linewidth=0.8)

    # Add value labels
    for bar, lat in zip(bars, latency):
        label = f'{lat}ms' if lat >= 1 else f'{lat*1000:.0f}\u00b5s'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                label, ha='center', va='bottom', fontsize=8, color=COLORS['text'])

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, fontsize=8, rotation=0)
    ax.set_ylabel('Latency per Query (ms)', fontsize=12, color=COLORS['text'])
    ax.set_title('Single Query Embedding Latency on Apple Silicon (M-series)',
                fontsize=14, fontweight='bold', color=COLORS['text'])

    # Add "doesn't matter" annotation
    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    ax.text(len(models)-1, 105, '100ms = still imperceptible to user',
            fontsize=9, color='gray', ha='right')

    ax.set_ylim(0, 120)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, '26_latency_comparison.png'), dpi=150)
    plt.close()
    print("Generated: 26_latency_comparison.png")


def chart_27_ram_comparison():
    """Chart 27: RAM usage comparison."""
    fig, ax = plt.subplots(figsize=(12, 6))

    models = [
        'potion-8M\n(current)',
        'potion-ret-32M',
        'mdbr-leaf-ir',
        'arctic-s / bge-s',
        'nomic-v1.5',
        'gte-modernbert',
        'Qwen3-0.6B',
        'Qwen3-4B',
        'Qwen3-8B',
    ]

    # RAM in MB (practical loaded, INT8 where applicable)
    ram_int8 = [15, 60, 50, 60, 250, 300, 1500, 8000, 16000]
    ram_fp32 = [50, 150, 100, 200, 800, 900, 3500, 16000, 32000]

    x = np.arange(len(models))
    width = 0.35

    bars1 = ax.bar(x - width/2, ram_int8, width, label='INT8 / Quantized',
                   color=COLORS['small'], edgecolor='white')
    bars2 = ax.bar(x + width/2, ram_fp32, width, label='FP32 (full precision)',
                   color=COLORS['medium'], alpha=0.6, edgecolor='white')

    # Add value labels for INT8
    for bar, ram in zip(bars1, ram_int8):
        label = f'{ram}MB' if ram < 1000 else f'{ram/1000:.1f}GB'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                label, ha='center', va='bottom', fontsize=7, color=COLORS['text'])

    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=8)
    ax.set_ylabel('RAM Usage (MB)', fontsize=12, color=COLORS['text'])
    ax.set_title('Memory Footprint by Model', fontsize=14, fontweight='bold', color=COLORS['text'])
    ax.set_yscale('log')
    ax.set_ylim(10, 50000)
    ax.legend(fontsize=10)

    # Add phone/laptop/GPU zones
    ax.axhline(y=500, color='orange', linestyle='--', alpha=0.4)
    ax.text(0.02, 520, 'Phone/Edge limit (~500MB)', transform=ax.get_yaxis_transform(),
            fontsize=8, color='orange')
    ax.axhline(y=4000, color='red', linestyle='--', alpha=0.4)
    ax.text(0.02, 4500, 'Laptop comfortable limit (~4GB)', transform=ax.get_yaxis_transform(),
            fontsize=8, color='red')

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, '27_ram_comparison.png'), dpi=150)
    plt.close()
    print("Generated: 27_ram_comparison.png")


def chart_28_predicted_locomo():
    """Chart 28: Predicted LoCoMo score improvements."""
    fig, ax = plt.subplots(figsize=(12, 7))

    configurations = [
        'Current\n(potion-8M)',
        'potion-ret-32M\n(drop-in)',
        'm2v-Qwen3\n(drop-in)',
        'Qwen3-0.6B\n(new backend)',
        'Nomic+Qwen3\n(dual model)',
        'Qwen3-0.6B +\nbetter reranker',
        'Qwen3-4B\n(GPU)',
        'EverMemOS\n(target)',
    ]

    # Predicted LoCoMo scores with uncertainty
    scores = [87.71, 88.2, 88.8, 91.0, 92.0, 93.0, 94.0, 92.77]
    lower = [87.38, 87.5, 87.8, 89.5, 90.0, 91.0, 92.5, 92.77]
    upper = [87.99, 89.0, 90.0, 92.5, 93.5, 94.5, 95.5, 92.77]

    colors = [
        COLORS['current'], COLORS['drop_in'], COLORS['drop_in'],
        COLORS['medium'], COLORS['large'], COLORS['large'],
        COLORS['gpu'], '#95a5a6',
    ]

    x = np.arange(len(configurations))
    bars = ax.bar(x, scores, color=colors, edgecolor='white', linewidth=0.8)

    # Add error bars
    for i, (s, lo, hi) in enumerate(zip(scores, lower, upper)):
        if i < len(configurations) - 1:  # Skip EverMemOS (no uncertainty)
            ax.plot([i, i], [lo, hi], color='black', linewidth=1.5, zorder=6)
            ax.plot([i-0.1, i+0.1], [lo, lo], color='black', linewidth=1.5, zorder=6)
            ax.plot([i-0.1, i+0.1], [hi, hi], color='black', linewidth=1.5, zorder=6)

    # Add value labels
    for bar, s in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{s:.1f}%', ha='center', va='bottom', fontsize=9,
                fontweight='bold', color=COLORS['text'])

    # EverMemOS reference line
    ax.axhline(y=92.77, color='#95a5a6', linestyle='--', alpha=0.7, zorder=1)
    ax.text(len(configurations)-0.5, 93.1, 'EverMemOS (92.77%)', fontsize=9,
            color='#95a5a6', ha='right')

    ax.set_xticks(x)
    ax.set_xticklabels(configurations, fontsize=8)
    ax.set_ylabel('Predicted LoCoMo Accuracy (%)', fontsize=12, color=COLORS['text'])
    ax.set_title('Predicted LoCoMo Scores by Configuration\n(with uncertainty ranges)',
                fontsize=14, fontweight='bold', color=COLORS['text'])
    ax.set_ylim(85, 97)

    # Labels for categories
    ax.annotate('Zero-code\nchanges', xy=(1, 85.5), fontsize=8, color=COLORS['drop_in'],
               ha='center', fontstyle='italic')
    ax.annotate('Engineering\nwork needed', xy=(4, 85.5), fontsize=8, color=COLORS['large'],
               ha='center', fontstyle='italic')

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, '28_predicted_locomo.png'), dpi=150)
    plt.close()
    print("Generated: 28_predicted_locomo.png")


def chart_29_cost_quality_tradeoff():
    """Chart 29: Monthly cost vs quality trade-off."""
    fig, ax = plt.subplots(figsize=(12, 7))

    configs = [
        ('Neuromem\n(current)', 12, 87.71, COLORS['current'], 200),
        ('+ potion-ret-32M', 12, 88.2, COLORS['drop_in'], 150),
        ('+ Qwen3-0.6B (CPU)', 14, 91.0, COLORS['medium'], 200),
        ('+ Qwen3-0.6B + reranker', 16, 93.0, COLORS['large'], 200),
        ('+ Qwen3-4B (GPU)', 45, 94.0, COLORS['gpu'], 180),
        ('EverMemOS', 260, 92.77, '#95a5a6', 200),
    ]

    for name, cost, score, color, size in configs:
        ax.scatter(cost, score, s=size, c=color, edgecolors='white',
                  linewidth=1.5, zorder=5)
        offset = (8, 5) if 'EverMemOS' not in name else (-80, -8)
        ax.annotate(name, (cost, score), textcoords="offset points",
                   xytext=offset, fontsize=9, color=COLORS['text'])

    ax.set_xlabel('Monthly Cost ($)', fontsize=12, color=COLORS['text'])
    ax.set_ylabel('LoCoMo Accuracy (%)', fontsize=12, color=COLORS['text'])
    ax.set_title('Cost vs. Quality Trade-Off\n(at 100 queries/day)',
                fontsize=14, fontweight='bold', color=COLORS['text'])
    ax.set_xlim(0, 300)
    ax.set_ylim(85, 97)

    # Add "sweet spot" region
    rect = mpatches.FancyBboxPatch((10, 90), 25, 5, boxstyle="round,pad=0.5",
                                    facecolor='green', alpha=0.1, edgecolor='green',
                                    linestyle='--', linewidth=1)
    ax.add_patch(rect)
    ax.text(22, 95.8, 'Sweet spot', fontsize=10, color='green', ha='center', fontstyle='italic')

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, '29_cost_quality_tradeoff.png'), dpi=150)
    plt.close()
    print("Generated: 29_cost_quality_tradeoff.png")


def chart_30_transformer_architecture():
    """Chart 30: Simplified transformer architecture diagram."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(6, 9.5, 'How a Transformer Embedding Model Works', fontsize=16,
            fontweight='bold', ha='center', color=COLORS['text'])
    ax.text(6, 9.0, '(simplified for understanding)', fontsize=11,
            ha='center', color='gray', fontstyle='italic')

    # Step 1: Input text
    box1 = mpatches.FancyBboxPatch((0.5, 7.5), 11, 1, boxstyle="round,pad=0.2",
                                    facecolor='#fff3e0', edgecolor='#e65100', linewidth=2)
    ax.add_patch(box1)
    ax.text(6, 8.2, 'Step 1: Input Text', fontsize=12, fontweight='bold', ha='center', color='#e65100')
    ax.text(6, 7.8, '"Jordan mentioned looking into adoption agencies last week"',
            fontsize=10, ha='center', fontstyle='italic', color=COLORS['text'])

    # Arrow
    ax.annotate('', xy=(6, 7.3), xytext=(6, 7.5), arrowprops=dict(arrowstyle='->', color='gray', lw=2))

    # Step 2: Tokenization
    box2 = mpatches.FancyBboxPatch((0.5, 5.8), 11, 1.3, boxstyle="round,pad=0.2",
                                    facecolor='#e3f2fd', edgecolor='#1565c0', linewidth=2)
    ax.add_patch(box2)
    ax.text(6, 6.85, 'Step 2: Tokenization (break into pieces)', fontsize=12,
            fontweight='bold', ha='center', color='#1565c0')
    ax.text(6, 6.3, '["Jordan"] ["mentioned"] ["looking"] ["into"] ["adoption"] ["agencies"] ["last"] ["week"]',
            fontsize=9, ha='center', family='monospace', color=COLORS['text'])
    ax.text(6, 5.95, 'Each token gets an initial number (like looking up a word in the dictionary)',
            fontsize=8, ha='center', fontstyle='italic', color='gray')

    # Arrow
    ax.annotate('', xy=(6, 5.5), xytext=(6, 5.8), arrowprops=dict(arrowstyle='->', color='gray', lw=2))

    # Step 3: Attention layers
    box3 = mpatches.FancyBboxPatch((0.5, 3.8), 11, 1.5, boxstyle="round,pad=0.2",
                                    facecolor='#e8f5e9', edgecolor='#2e7d32', linewidth=2)
    ax.add_patch(box3)
    ax.text(6, 5.05, 'Step 3: Self-Attention (the "transformer" magic)', fontsize=12,
            fontweight='bold', ha='center', color='#2e7d32')
    ax.text(6, 4.55, 'Each word looks at every other word to understand context:',
            fontsize=10, ha='center', color=COLORS['text'])
    ax.text(6, 4.1, '"adoption" + "agencies" together = researching adoption (not just the word "adoption" alone)',
            fontsize=9, ha='center', fontstyle='italic', color=COLORS['text'])

    # Arrow
    ax.annotate('', xy=(6, 3.5), xytext=(6, 3.8), arrowprops=dict(arrowstyle='->', color='gray', lw=2))

    # Step 4: Pooling
    box4 = mpatches.FancyBboxPatch((0.5, 2.2), 11, 1.1, boxstyle="round,pad=0.2",
                                    facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=2)
    ax.add_patch(box4)
    ax.text(6, 3.05, 'Step 4: Pooling (combine into one vector)', fontsize=12,
            fontweight='bold', ha='center', color='#7b1fa2')
    ax.text(6, 2.55, 'All 8 context-aware token vectors → average → single vector of 256-1024 numbers',
            fontsize=10, ha='center', color=COLORS['text'])

    # Arrow
    ax.annotate('', xy=(6, 1.9), xytext=(6, 2.2), arrowprops=dict(arrowstyle='->', color='gray', lw=2))

    # Step 5: Output embedding
    box5 = mpatches.FancyBboxPatch((0.5, 0.5), 11, 1.2, boxstyle="round,pad=0.2",
                                    facecolor='#fce4ec', edgecolor='#c62828', linewidth=2)
    ax.add_patch(box5)
    ax.text(6, 1.4, 'Step 5: The Embedding (a list of numbers)', fontsize=12,
            fontweight='bold', ha='center', color='#c62828')
    ax.text(6, 0.9, '[0.23, -0.81, 0.45, 0.12, -0.67, 0.33, ...] (256 to 4096 numbers)',
            fontsize=10, ha='center', family='monospace', color=COLORS['text'])
    ax.text(6, 0.6, 'Similar sentences → similar number lists → the computer can find matches!',
            fontsize=9, ha='center', fontstyle='italic', color='gray')

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, '30_transformer_architecture.png'), dpi=150)
    plt.close()
    print("Generated: 30_transformer_architecture.png")


def chart_31_reingestion_time():
    """Chart 31: Re-ingestion time at different scales."""
    fig, ax = plt.subplots(figsize=(12, 6))

    scales = ['5,000\nmessages', '10,000\nmessages', '50,000\nmessages', '100,000\nmessages', '1,000,000\nmessages']
    scale_nums = [5000, 10000, 50000, 100000, 1000000]

    # Time in minutes
    model2vec_time = [s/25000/60 for s in scale_nums]  # 25000/sec
    small_onnx_time = [s/200/60 for s in scale_nums]   # 200/sec
    medium_time = [s/80/60 for s in scale_nums]         # 80/sec
    qwen06_time = [s/20/60 for s in scale_nums]         # 20/sec

    x = np.arange(len(scales))
    width = 0.2

    ax.bar(x - 1.5*width, model2vec_time, width, label='Model2Vec (any)', color=COLORS['drop_in'])
    ax.bar(x - 0.5*width, small_onnx_time, width, label='33M model (ONNX)', color=COLORS['small'])
    ax.bar(x + 0.5*width, medium_time, width, label='137M model (PyTorch)', color=COLORS['medium'])
    ax.bar(x + 1.5*width, qwen06_time, width, label='Qwen3-0.6B (CPU)', color=COLORS['large'])

    ax.set_xticks(x)
    ax.set_xticklabels(scales, fontsize=9)
    ax.set_ylabel('Re-embedding Time (minutes)', fontsize=12, color=COLORS['text'])
    ax.set_title('Time to Re-embed All Messages When Switching Models',
                fontsize=14, fontweight='bold', color=COLORS['text'])
    ax.set_yscale('log')
    ax.legend(fontsize=9)

    # Add "acceptable" line
    ax.axhline(y=60, color='orange', linestyle='--', alpha=0.5)
    ax.text(0.02, 65, '1 hour (run overnight)', fontsize=8, color='orange')

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, '31_reingestion_time.png'), dpi=150)
    plt.close()
    print("Generated: 31_reingestion_time.png")


if __name__ == '__main__':
    chart_25_quality_vs_params()
    chart_26_latency_comparison()
    chart_27_ram_comparison()
    chart_28_predicted_locomo()
    chart_29_cost_quality_tradeoff()
    chart_30_transformer_architecture()
    chart_31_reingestion_time()
    print("\nAll embedding guide charts generated!")
