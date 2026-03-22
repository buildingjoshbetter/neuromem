#!/usr/bin/env python3
"""
Rebuild Benchmark DBs with Qwen3-Embedding-0.6B (Phase 1)
==========================================================

Copies the 10 LoCoMo benchmark databases and re-embeds all messages
using Qwen/Qwen3-Embedding-0.6B (1024-dim) instead of Model2Vec (256-dim).

The original DBs in benchmark_dbs/ are NOT modified. New DBs are written
to benchmark_dbs_phase1/.

Usage:
    python rebuild_dbs_phase1.py              # Rebuild all 10
    python rebuild_dbs_phase1.py --conv 0 3   # Rebuild only conv 0 and 3

Author: Joshua Adler
Date: March 22, 2026
"""

import argparse
import shutil
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from neuromem.vector_search import (
    set_embedding_model,
    get_model,
    init_vec_table,
    build_vectors,
    build_separation_vectors,
    _embedding_dim,
)


SRC_DIR = Path(__file__).parent / "benchmark_dbs"
DST_DIR = Path(__file__).parent / "benchmark_dbs_phase1"


def rebuild_db(src_path: Path, dst_path: Path) -> dict:
    """Copy a DB and rebuild its vector tables with the current embedding model."""
    # Copy the DB file (skip WAL/SHM — checkpoint first if needed)
    shutil.copy2(src_path, dst_path)

    # Also copy WAL/SHM if they exist (for DBs in WAL mode)
    for suffix in ("-wal", "-shm"):
        wal = Path(str(src_path) + suffix)
        if wal.exists():
            shutil.copy2(wal, Path(str(dst_path) + suffix))

    conn = sqlite3.connect(str(dst_path))

    # Load sqlite-vec extension (needed to drop/create vec0 virtual tables)
    import sqlite_vec
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    # Checkpoint WAL to main DB, then switch to DELETE journal mode
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.execute("PRAGMA journal_mode=DELETE")

    # Drop old vector tables
    conn.execute("DROP TABLE IF EXISTS vec_messages")
    conn.execute("DROP TABLE IF EXISTS vec_messages_sep")
    conn.commit()

    # Remove leftover WAL/SHM files
    for suffix in ("-wal", "-shm"):
        f = Path(str(dst_path) + suffix)
        if f.exists():
            f.unlink()

    # Recreate vector tables with new dimension
    init_vec_table(conn)

    # Count messages
    msg_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]

    # Rebuild vectors
    t0 = time.time()
    n_vec = build_vectors(conn)
    t_vec = time.time() - t0

    # Rebuild separation vectors
    t1 = time.time()
    n_sep = build_separation_vectors(conn)
    t_sep = time.time() - t1

    conn.close()

    return {
        "messages": msg_count,
        "vectors": n_vec,
        "sep_vectors": n_sep,
        "vec_time": t_vec,
        "sep_time": t_sep,
    }


def main():
    parser = argparse.ArgumentParser(description="Rebuild benchmark DBs with Qwen3 embeddings")
    parser.add_argument("--conv", type=int, nargs="*", default=None,
                        help="Conversation indices to rebuild (default: all 0-9)")
    args = parser.parse_args()

    conv_ids = args.conv if args.conv is not None else list(range(10))

    # Switch to Qwen3 embedding model
    print("Setting embedding model to qwen3 (Qwen/Qwen3-Embedding-0.6B, 1024-dim)")
    set_embedding_model("qwen3")

    # Pre-load model so we can report load time
    print("Loading model...")
    t_load = time.time()
    model = get_model()
    t_load = time.time() - t_load
    print(f"Model loaded in {t_load:.1f}s")

    # Create output directory
    DST_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nSource: {SRC_DIR}")
    print(f"Destination: {DST_DIR}")
    print(f"Conversations to rebuild: {conv_ids}")
    print()

    total_msgs = 0
    total_time = 0

    for ci in conv_ids:
        src = SRC_DIR / f"neuromem_locomo_{ci}.db"
        dst = DST_DIR / f"neuromem_locomo_{ci}.db"

        if not src.exists():
            print(f"  SKIP: {src} not found")
            continue

        print(f"  Rebuilding conv {ci}...", end=" ", flush=True)
        t0 = time.time()
        stats = rebuild_db(src, dst)
        elapsed = time.time() - t0

        total_msgs += stats["messages"]
        total_time += elapsed

        print(f"{stats['messages']} msgs, "
              f"vectors: {stats['vec_time']:.1f}s, "
              f"sep: {stats['sep_time']:.1f}s, "
              f"total: {elapsed:.1f}s")

    print(f"\nDone! {total_msgs} messages re-embedded in {total_time:.1f}s")
    print(f"New DBs in: {DST_DIR}")


if __name__ == "__main__":
    main()
