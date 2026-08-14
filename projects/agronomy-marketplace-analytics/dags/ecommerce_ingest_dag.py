"""Airflow DAG: ecommerce ingest -> ClickHouse marts -> quality checks.

Optional for portfolio demos. Local users can run scripts/run_pipeline.py instead.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

# When copied into an Airflow dags folder, adjust this path or install the package.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from checks.data_quality import main as run_quality_checks
from scripts.ch_utils import build_marts, create_schema, get_client, load_orders_from_csv


def task_create_schema() -> None:
    create_schema(get_client())


def task_load_orders() -> None:
    n = load_orders_from_csv(get_client())
    print(f"Loaded {n} rows")


def task_build_marts() -> None:
    build_marts(get_client())


def task_quality() -> None:
    code = run_quality_checks()
    if code != 0:
        raise RuntimeError("Data quality checks failed")


with DAG(
    dag_id="ecommerce_clickhouse_pipeline",
    description="Portfolio DAG: CSV orders to ClickHouse marts with quality checks",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["portfolio", "clickhouse", "ecommerce"],
) as dag:
    create = PythonOperator(task_id="create_schema", python_callable=task_create_schema)
    load = PythonOperator(task_id="load_orders", python_callable=task_load_orders)
    marts = PythonOperator(task_id="build_marts", python_callable=task_build_marts)
    quality = PythonOperator(task_id="data_quality", python_callable=task_quality)

    create >> load >> marts >> quality
