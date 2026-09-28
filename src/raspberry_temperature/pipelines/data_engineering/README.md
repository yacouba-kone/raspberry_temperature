# Pipeline : data engineering

Préparation des données de température mesurées par le Raspberry Pi.

## Rôle

Ce pipeline transforme les données brutes (fichier JSON historique ou messages
IoT) en un DataFrame exploitable, soit par le pipeline d'entraînement, soit par
le pipeline d'envoi des prédictions.

## Nœuds (`nodes.py`)

| Nœud | Entrées | Sorties | Description |
| --- | --- | --- | --- |
| `load_train_data` | `raw_data` | `historical_data` | Charge et copie les mesures historiques (`01_raw/IntroMLops-1.json`) |
| `clean_data` | `historical_data` | `cleaned_data` | Filtre `temperature >= 30 °C` puis calcule `ratio = intensity / humidity` |
| `clean_data_prod` | `message_broker` | `cleaned_data_prod` | Décode les messages IoT Azure, normalise `EventProcessedUtcTime` en UTC, conserve les colonnes `temperature` / `humidity` / `intensity`, filtre `humidity >= 30` et calcule `ratio` |

Le décorateur `log_running_time` journalise la durée d'exécution d'un nœud ; il
est actuellement désactivé sur `clean_data`.

## Pipelines (`pipeline.py`)

| Clé du registre | Tags | Chaîne de nœuds |
| --- | --- | --- |
| `dev` | `de_dev` | `raw_data` -> `historical_data` -> `cleaned_data` |
| `prod` | `de_prod` | `message_broker` -> `cleaned_data_prod` |

Ces variantes sont assemblées par `raspberry_temperature/pipeline_registry.py` :
la variante `dev` est exposée sous la clé `de`, la variante `prod` est combinée
avec le pipeline `share_data` sous la clé `prod`.

## Exécution

```bash
uv run kedro run --pipeline de      # nettoyage des données historiques
uv run kedro run --pipeline prod    # nettoyage prod puis envoi des prédictions
```

## Tests

Voir `src/tests/pipelines/data_engineering/test_nodes.py`.

