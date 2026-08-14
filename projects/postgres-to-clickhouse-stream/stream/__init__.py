"""Stream config from environment."""

from __future__ import annotations

import os


def env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing required env var: {name}")
    return value


PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5433"))
PG_USER = os.getenv("PG_USER", "stream")
PG_PASSWORD = os.getenv("PG_PASSWORD", "stream")
PG_DATABASE = os.getenv("PG_DATABASE", "marketplace")

CH_HOST = os.getenv("CH_HOST", "localhost")
CH_PORT = int(os.getenv("CH_PORT", "8124"))
CH_USER = os.getenv("CH_USER", "default")
CH_PASSWORD = os.getenv("CH_PASSWORD", "stream")

STREAM_NAME = os.getenv("STREAM_NAME", "marketplace_orders")
STREAM_POLL_SECONDS = float(os.getenv("STREAM_POLL_SECONDS", "2"))
STREAM_BATCH_SIZE = int(os.getenv("STREAM_BATCH_SIZE", "500"))
