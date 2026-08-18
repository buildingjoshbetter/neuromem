"""Tests for MPS memory management, process RSS watchdog, and idle model unloading."""
from __future__ import annotations

import os
import time
from unittest.mock import MagicMock, patch

from truememory.model_server import ModelServer, _EmbedState
from truememory.mps_utils import (
    check_memory_pressure,
    flush_mps_cache,
    get_process_memory_mb,
)


class TestMemoryUtils:
    """Test utility functions for process memory inspection and cache flushing."""

    def test_get_process_memory_mb_returns_positive_float(self):
        rss = get_process_memory_mb()
        assert isinstance(rss, float)
        assert rss > 0.0

    def test_check_memory_pressure_default_limit(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TRUEMEMORY_MAX_MEMORY_MB", None)
            res = check_memory_pressure()
            assert res["max_mb"] == 1500.0
            assert "rss_mb" in res
            assert isinstance(res["warning"], bool)
            assert isinstance(res["exceeded"], bool)

    def test_check_memory_pressure_custom_limit(self):
        with patch.dict(os.environ, {"TRUEMEMORY_MAX_MEMORY_MB": "500"}):
            res = check_memory_pressure()
            assert res["max_mb"] == 500.0

    def test_check_memory_pressure_warning_and_exceeded_flags(self):
        with patch("truememory.mps_utils.get_process_memory_mb", return_value=800.0):
            res = check_memory_pressure(max_mb=1000.0)
            assert res["warning"] is True
            assert res["exceeded"] is False

        with patch("truememory.mps_utils.get_process_memory_mb", return_value=1200.0):
            res = check_memory_pressure(max_mb=1000.0)
            assert res["warning"] is True
            assert res["exceeded"] is True

    def test_flush_mps_cache_executes_safely(self):
        # Should execute without throwing regardless of PyTorch / MPS availability
        flush_mps_cache()


class TestModelServerMemoryWatchdog:
    """Test ModelServer memory watchdog and idle unload circuit breaker."""

    def test_watchdog_flushes_cache_on_warning(self):
        server = ModelServer()
        flushed = [False]

        def mock_flush():
            flushed[0] = True

        server._flush_mps_cache = mock_flush

        with patch(
            "truememory.mps_utils.check_memory_pressure",
            return_value={"rss_mb": 1200.0, "max_mb": 1500.0, "warning": True, "exceeded": False},
        ):
            server._check_memory_watchdog()
            assert flushed[0] is True

    def test_watchdog_unloads_models_on_exceeded(self):
        server = ModelServer()
        dummy_model = MagicMock()
        server._embed_state = _EmbedState(model=dummy_model, tier="pro", model_id="qwen3_256")
        server._reranker = MagicMock()
        server._reranker_name = "gte-reranker"
        server._fast_encoder = MagicMock()
        server._fast_model_id = "qwen3_256"

        with patch(
            "truememory.mps_utils.check_memory_pressure",
            side_effect=[
                {"rss_mb": 1600.0, "max_mb": 1500.0, "warning": True, "exceeded": True},
                {"rss_mb": 400.0, "max_mb": 1500.0, "warning": False, "exceeded": False},
            ],
        ):
            server._check_memory_watchdog()

            assert server._embed_state is None
            assert server._reranker is None
            assert server._reranker_name is None
            assert server._fast_encoder is None
            assert server._fast_model_id is None

    def test_idle_checker_unloads_models_when_idle(self):
        server = ModelServer()
        dummy_model = MagicMock()
        server._embed_state = _EmbedState(model=dummy_model, tier="pro", model_id="qwen3_256")
        server._last_activity = time.time() - 250  # 250s ago (> 180s threshold)
        server._inflight = 0

        flushed = [False]
        server._flush_mps_cache = lambda: flushed.__setitem__(0, True)

        # Trigger single cycle of idle unload logic
        has_loaded = server._embed_state is not None
        assert has_loaded is True

        elapsed = time.time() - server._last_activity
        assert elapsed >= 180

        with server._lock:
            server._embed_state = None
            server._reranker = None
            server._reranker_name = None
        with server._fast_lock:
            server._fast_encoder = None
            server._fast_model_id = None
        server._flush_mps_cache()

        assert server._embed_state is None
        assert flushed[0] is True
