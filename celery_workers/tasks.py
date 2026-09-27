from celery_workers.celery import app
import subprocess
import json
from pathlib import Path
import os
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Configure logger
import logging
logger = logging.getLogger()

# Configure saving path
# We're working relative to the root directory
#PATH_TO_SAVE_BROKER_MESSAGE = './data/01_raw/message_from_message_broker.json'
PATH_TO_SAVE_BROKER_MESSAGE = (
    PROJECT_ROOT / "data" / "01_raw" / "message_from_message_broker.json"
)

DUCKDB_DIR = PROJECT_ROOT / "data" / "07_model_output"
DUCKDB_DIR.mkdir(parents=True, exist_ok=True)

#def process_message_with_kedro(message: str):
#    json_message = json.loads(message)
#    with open(PATH_TO_SAVE_BROKER_MESSAGE, 'w') as json_file:
#        json.dump(json_message, json_file)
#    # Lance le pipeline Kedro "prod" via uv dans un processus séparé
#    # et capture sa sortie standard (stdout).
#    proc = subprocess.Popen(
#        ["uv", "run", "kedro", "run", "--pipeline=prod"],
#        stdout=subprocess.PIPE)
#    (out, err) = proc.communicate()
#    logger.info(f'This is kedro output for message : {message}')
#    _format_console_logs(out)
#    return str(f"work for message is done")

def create_kedro_credentials():
    credentials_dir = PROJECT_ROOT / "conf" / "base"
    credentials_dir.mkdir(parents=True, exist_ok=True)

    DUCKDB_DIR = PROJECT_ROOT / "data" / "07_model_output"
    DUCKDB_DIR.mkdir(parents=True, exist_ok=True)

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
    PATH_TO_SAVE_BROKER_MESSAGE.parent.mkdir(parents=True, exist_ok=True)

    with open(PATH_TO_SAVE_BROKER_MESSAGE, "w", encoding="utf-8") as json_file:
        json.dump([json_message], json_file, ensure_ascii=False, indent=2)

    logger.info("Message sauvegardé dans %s", PATH_TO_SAVE_BROKER_MESSAGE)

    DUCKDB_DIR = PROJECT_ROOT / "data" / "07_model_output"
    DUCKDB_DIR.mkdir(parents=True, exist_ok=True)

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


def _format_console_logs(console_output: bytes) -> None:
    logs = console_output.decode('latin-1').split('\n')
    for log in logs:
        logger.info(log)