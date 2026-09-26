from pathlib import Path
import yaml
from kedro_datasets.pickle import PickleDataset

ROOT = Path(__file__).resolve().parent

with open(ROOT / "conf/base/credentials.yml", "r", encoding="utf-8") as f:
    credentials = yaml.safe_load(f)

dataset = PickleDataset(
    filepath="abfs://raspberry-temperature/06_models/model_temperature.pkl",
    credentials=credentials["azure_blob"],
)

model = dataset.load()

print("✅ Modèle chargé depuis Azure Blob")
print("Type :", type(model))