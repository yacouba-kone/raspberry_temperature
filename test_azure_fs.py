from pathlib import Path
import yaml
from adlfs import AzureBlobFileSystem

ROOT = Path(__file__).resolve().parent

with open(ROOT / "conf/base/credentials.yml", "r", encoding="utf-8") as f:
    credentials = yaml.safe_load(f)

config = credentials["azure_storage"]

fs = AzureBlobFileSystem(
    account_name="raspberry",
    connection_string=config["connection_string"],
)

path = f"{config['container_name']}/06_models/model_temperature.pkl"

print("Connexion Azure FS OK")
print("Fichier existe :", fs.exists(path))

print("\nFichiers dans 06_models :")
for file in fs.ls(f"{config['container_name']}/06_models"):
    print(" -", file)