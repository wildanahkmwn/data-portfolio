"""Airflow DAG: Postgres seed -> ClickHouse sync -> marts -> quality checks."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from checks.data_quality import main as run_quality_checks
from scripts.ch_utils import (
    build_marts,
    create_schema,
    get_client,
    reset_sink,
    sync_all,
)
from scripts.pg_utils import create_source_schema, get_connection, load_orders_from_csv


def task_seed_postgres() -> None:
    with get_connection() as pg:
        create_source_schema(pg)
        n = load_orders_from_csv(pg)
        print(f"Seeded {n} Postgres rows")


def task_sync_clickhouse() -> None:
    ch = get_client()
    create_schema(ch)
    reset_sink(ch)
    with get_connection() as pg:
        n = sync_all(pg, ch)
        print(f"Synced {n} rows to ClickHouse")


def task_build_marts() -> None:
    build_marts(get_client())


def task_quality() -> None:
    code = run_quality_checks()
    if code != 0:
        raise RuntimeError("Data quality checks failed")


with DAG(
    dag_id="ecommerce_clickhouse_pipeline",
    description="Portfolio DAG: Postgres orders to ClickHouse marts with quality checks",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["portfolio", "clickhouse", "postgres", "ecommerce"],
) as dag:
    seed = PythonOperator(task_id="seed_postgres", python_callable=task_seed_postgres)
    sync = PythonOperator(
        task_id="sync_clickhouse", python_callable=task_sync_clickhouse
    )
    marts = PythonOperator(task_id="build_marts", python_callable=task_build_marts)
    quality = PythonOperator(task_id="data_quality", python_callable=task_quality)

    seed >> sync >> marts >> quality
