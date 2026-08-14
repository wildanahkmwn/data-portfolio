"""Continuous Postgres -> ClickHouse sync for new marketplace orders."""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ch_utils import build_marts, create_schema, get_client, sync_once
from scripts.pg_utils import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("agro.stream")
POLL_SECONDS = float(os.getenv("STREAM_POLL_SECONDS", "2"))


def run_forever() -> None:
    ch = get_client()
    create_schema(ch)
    log.info("stream worker ready")
    while True:
        try:
            with get_connection() as pg:
                n = sync_once(pg, ch)
                if n:
                    build_marts(ch)
                    log.info("synced=%s", n)
        except Exception:
            log.exception("sync loop error; retrying")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run_forever()
