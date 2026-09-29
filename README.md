# Raspberry Temperature

## Introduction

Ce projet met en oeuvre une chaîne MLOps complète autour d'un capteur
Raspberry Pi : réception des mesures (température, humidité, intensité
lumineuse) depuis Azure Event Hub, nettoyage des données, entraînement d'un
modèle de régression linéaire qui prédit la température, puis écriture des
prédictions dans une base de données.

L'orchestration des traitements est assurée par **Kedro**, le suivi des
expériences par **MLflow**, et l'industrialisation par **Azure** (Event Hub,
Service Bus, Blob Storage, Azure SQL, Container Apps). La gestion des
dépendances et des environnements repose sur **uv**.

## Architecture

```
Raspberry / IoT
      |
      v
 Azure Event Hub
      |
      v
 raspberry-consumer   (consumer/)        -> met le message en file
      |
      v
 Azure Service Bus
      |
      v
 raspberry-celery     (celery_workers/)  -> lance le pipeline Kedro
      |
      v
 Kedro : pipeline "prod"
      |
      v
 Azure Blob Storage + Azure SQL / DuckDB
```

| Composant | Rôle |
| --- | --- |
| `consumer/` | Client Azure Event Hub : reçoit chaque mesure et la publie dans la file Azure Service Bus via Celery (`process_message_with_kedro.delay`) |
| `celery_workers/` | Worker Celery rattaché à Azure Service Bus : écrit le message reçu dans `data/01_raw/message_from_message_broker.json`, génère les credentials Azure, puis exécute `uv run kedro run --pipelines prod` |
| `src/raspberry_temperature/` | Code du projet Kedro : pipelines, nœuds, datasets personnalisés, connexion Azure SQL |
| `conf/` | Configuration Kedro : catalogue de datasets, paramètres, credentials, logging (`base`, `local`, `train`, `dev`, `pprd`, `prd`) |
| `data/` | Données de travail (01_raw, 02_intermediate, 05_model_input, 06_models, 07_model_output, 08_reporting) |
| `notebooks/` | Analyse exploratoire (`EDA.ipynb`) |
| `mlflow.db` / `mlartifacts/` | Backend local de suivi MLflow et artefacts (graphiques, modèles) |
| `Dockerfile` | Image du consommateur Event Hub (`uv run python consumer/consumer.py`) |
| `Dockerfile.celery` | Image du worker Celery, avec ODBC Driver 18 (nécessaire pour Azure SQL) |
| `azure-pipelines.yml` | Chaîne CI/CD Azure DevOps : tests, build des images, déploiement Azure Container Apps |

## Arborescence du code Kedro

```
src/
├── create_azure_sql_table.py        # script de création de la table Azure SQL
├── raspberry_temperature/
│   ├── azure_sql.py                 # moteur SQLAlchemy authentifié (token Entra ID)
│   ├── pipeline_registry.py         # registre des pipelines (point d'entrée Kedro)
│   ├── pipeline.py                  # ancienne fabrique de pipelines (commentée)
│   ├── run.py                       # exécution du projet empaqueté
│   ├── datasets/
│   │   └── azure_sql_dataset.py     # dataset Kedro Azure SQL
│   └── pipelines/
│       ├── data_engineering/        # nettoyage des données (dev et prod)
│       ├── data_sciences/           # entraînement du modèle (MLflow)
│       └── share_data/              # envoi des prédictions en base
└── tests/                           # tests unitaires pytest
```

Chaque dossier de pipeline dispose de son propre `README.md` détaillant les
nœuds, les entrées/sorties et les tags.

## Pipelines disponibles

Les pipelines sont déclarés dans `src/raspberry_temperature/pipeline_registry.py`.

| Clé (`--pipeline`) | Contenu | Description |
| --- | --- | --- |
| `de` | data engineering `dev` | Nettoie les données historiques (`raw_data` -> `cleaned_data`) |
| `training` | data sciences | Découpe, entraîne et évalue le modèle (`model_temperature`) |
| `prod` | data engineering `prod` + share data `prod` | Nettoie les messages IoT et écrit les prédictions dans Azure SQL |
| `pprd` | data engineering `prod` + share data `pprd` | Même chaîne, table de pré-production |
| `__default__` | `de` + `training` | Pipeline lancé par défaut (`kedro run`) |

```bash
uv run kedro run                                        # pipeline par défaut
uv run kedro run --pipeline de                          # nettoyage des données historiques
uv run kedro run --pipeline training                    # entraînement du modèle
uv run kedro run --pipeline prod                        # chaîne de production
uv run kedro run --pipeline pprd                        # chaîne de pré-production
```

## Prérequis

- Python 3.14 et [uv](https://docs.astral.sh/uv/)
- ODBC Driver 18 for SQL Server (connexion Azure SQL)
- Azure CLI (`az login`) ou identité managée pour l'authentification Entra ID
- Un accès Azure : Event Hub, Service Bus, Storage Account, Azure SQL Database
- Un serveur MLflow local (`http://127.0.0.1:5000`) pour le suivi des runs

## Installation

```bash
git clone <url-du-depot>
cd raspberry_temperature
uv sync --frozen
uv run kedro info                       # vérifie l'installation de Kedro
uv run kedro catalog describe-datasets  # valide le catalogue de datasets
```

## Configuration

| Fichier | Contenu |
| --- | --- |
| `conf/base/catalog.yml` | Datasets Kedro : `raw_data`, `message_broker`, `cleaned_data`, `x_train`, ..., `model_temperature`, `output_table_dev` (DuckDB), `output_table_prod` (Azure SQL) |
| `conf/base/parameters.yml` | `features` (`intensity`, `humidity`, `ratio`), `label_name` (`temperature`), `test_size`, `random_state` |
| `conf/local/credentials.yml` | Secrets locaux (non versionnés) |
| `conf/base/logging.yml` | Configuration de la journalisation par environnement |

En local, le consommateur et le worker lisent leurs secrets dans
`conf/base/credentials.yml` (clés `azure_blob`, `duckdb_credentials` et
`dev-azure` : `message_broker`, `workers_queue`).

En environnement déployé (`PY_ENV` différent de `local`), les valeurs
proviennent de variables d'environnement :

| Variable | Usage |
| --- | --- |
| `CONSUMER_CONNECTION_STR`, `CONSUMER_GROUP`, `CONSUMER_EVENT_HUB_NAME` | Connexion au hub d'événements Azure |
| `ASBUS_POLICY_NAME`, `ASBUS_PRIMARY_KEY`, `ASBUS_NAMESPACE` | Connexion à Azure Service Bus (broker Celery) |
| `AZURE_STORAGE_ACCOUNT_NAME`, `AZURE_STORAGE_ACCOUNT_KEY` | Accès au Blob Storage utilisé par Kedro |
| `PY_ENV` | Sélection du mode de configuration (`local` par défaut) |

> Aucun secret ne doit être committé : utilisez `conf/local/` ou les variables
> d'environnement.

## Suivi des expériences (MLflow)

Le nœud `train_model` enregistre chaque entraînement dans l'expérience
`raspberry-temperature` :

- paramètres : `model_type`, `best_fit_intercept` ;
- métriques : `r2_score`, `rmse`, `mse`, `explained_variance` ;
- artefacts : graphiques (`plots/residual_analysis.png`,
  `plots/actual_vs_predicted.png`) et modèle sérialisé (`model`).

```bash
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db   # http://127.0.0.1:5000
```

## Base de données de sortie

- **Développement** : `output_table_dev` écrit dans DuckDB
  (`data/07_model_output/raspberry_temperature.duckdb`, table `training_table`).
- **Production** : `output_table_prod` écrit dans Azure SQL
  (`raspberry-sql.database.windows.net`, base `raspberry-temperature`, table
  `dbo.training_table_prod`) via le dataset `AzureSQLTableDataset`. La table doit
  être créée au préalable :

```bash
uv run python src/create_azure_sql_table.py
```

L'authentification utilise un token Microsoft Entra ID (`DefaultAzureCredential`)
transmis à pyodbc : aucun login ni mot de passe n'est stocké dans le code.

## Tests

```bash
uv run pytest                                           # tous les tests
uv run pytest src/tests -q                              # exécution concise
uv run pytest src/tests/pipelines/data_engineering -q   # un pipeline précis
```

Les tests couvrent le nettoyage des données (`clean_data`, `clean_data_prod`),
le découpage des jeux d'entraînement (`split_data`) et la mise au format des
prédictions (`predict`). Le détail figure dans les `README.md` de
`src/tests/pipelines/`.

## Intégration et déploiement continus

`azure-pipelines.yml` (déclenché sur la branche `develop`) exécute :

1. l'installation de Python 3.14 et de `uv`, puis `uv sync --frozen` ;
2. la vérification de l'environnement Kedro (`kedro info`,
   `kedro catalog describe-datasets`) avec des credentials dédiés à la CI ;
3. la suite de tests (`uv run pytest`) ;
4. le build et le push des images `raspberry-consumer` et `raspberry-celery`
   vers Azure Container Registry ;
5. la mise à jour des Container Apps `raspberry-consumer` et `raspberry-celery`.

Build et publication manuels :

```bash
docker build -t raspberry-consumer:latest .
docker build -f Dockerfile.celery -t raspberry-celery:latest .

az acr login --name raspberryregistry
docker tag raspberry-consumer:latest raspberryregistry.azurecr.io/raspberry-consumer:latest
docker push raspberryregistry.azurecr.io/raspberry-consumer:latest
```

## Limitations connues

- Les seuils métier sont codés en dur dans les nœuds (température >= 30 °C,
  humidité >= 30) ; certains commentaires historiques mentionnent encore 60 %.


