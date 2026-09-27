from celery_workers.celery import app

import json
import logging
import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

logger = logging.getLogger()

PATH_TO_SAVE_BROKER_MESSAGE = (
    PROJECT_ROOT
    / "data"
    / "01_raw"
    / "message_from_message_broker.json"
)

DUCKDB_DIR = PROJECT_ROOT / "data" / "07_model_output"
DUCKDB_DIR.mkdir(parents=True, exist_ok=True)


def create_kedro_credentials():
    credentials_dir = PROJECT_ROOT / "conf" / "base"
    credentials_dir.mkdir(parents=True, exist_ok=True)

    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")

    if not account_name or not account_key:
        raise RuntimeError(
            "Variables Azure Storage manquantes : "
            "AZURE_STORAGE_ACCOUNT_NAME et AZURE_STORAGE_ACCOUNT_KEY"
        )

    credentials_file = credentials_dir / "credentials.yml"

    credentials_file.write_text(
        f"""azure_blob:
  account_name: {account_name}
  account_key: "{account_key}"

duckdb_credentials:
  con: "duckdb:///data/07_model_output/raspberry_temperature.duckdb"
""",
        encoding="utf-8",
    )

    logger.info("Credentials Kedro Azure Blob configurés.")


@app.task
def process_message_with_kedro(message: str):
    create_kedro_credentials()

    json_message = json.loads(message)

    PATH_TO_SAVE_BROKER_MESSAGE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        PATH_TO_SAVE_BROKER_MESSAGE,
        "w",
        encoding="utf-8",
    ) as json_file:
        json.dump(
            [json_message],
            json_file,
            ensure_ascii=False,
            indent=2,
        )

    logger.info(
        "Message sauvegardé dans %s",
        PATH_TO_SAVE_BROKER_MESSAGE,
    )

    proc = subprocess.run(
        ["uv", "run", "kedro", "run", "--pipelines", "prod"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )

    logger.info("===== KEDRO STDOUT =====")
    logger.info(proc.stdout)

    logger.info("===== KEDRO STDERR =====")
    logger.error(proc.stderr)

    logger.info("KEDRO RETURN CODE = %s", proc.returncode)

    if proc.returncode != 0:
        raise RuntimeError(
            f"Kedro a échoué avec le code {proc.returncode}\n"
            f"STDERR:\n{proc.stderr}"
        )

    return "work for message is done"

