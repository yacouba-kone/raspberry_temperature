# Pipeline : share data

Application du modèle entraîné aux données de production et écriture des
prédictions dans la base de destination.

## Rôle

Ce pipeline ne fait pas d'entraînement : il réutilise le modèle
`model_temperature` et les données nettoyées `cleaned_data_prod` pour produire
le DataFrame des prédictions (`y_pred`, `Time`) et le persister en base.

## Nœuds (`nodes.py`)

| Nœud | Entrées | Sorties | Description |
| --- | --- | --- | --- |
| `predict` | `model_temperature`, `cleaned_data_prod`, `params:features` | `output_table_prod` / `output_table_pprd` | Applique le modèle aux colonnes `features`, renvoie les prédictions avec l'horodatage courant |

## Pipelines (`pipeline.py`)

| Clé du registre | Tags | Destination |
| --- | --- | --- |
| `prod` | `send_data_prod` | `output_table_prod` : Azure SQL, table `dbo.training_table_prod` (dataset `AzureSQLTableDataset`, `if_exists: append`) |
| `pprd` | `send_data_pprd` | `output_table_pprd` : table de pré-production |

Dans `pipeline_registry.py`, chaque variante est combinée avec le nettoyage de
production (`de_pipeline_prod`) sous les clés `prod` et `pprd`.

## Prérequis

- le modèle `model_temperature` doit exister dans le catalogue Kedro ;
- les données `cleaned_data_prod` doivent être disponibles (pipeline de data
  engineering en mode `prod`) ;
- pour Azure SQL : table créée par `src/create_azure_sql_table.py` et
  authentification Entra ID opérationnelle (`az login` en local ou identité
  managée dans Azure).

## Exécution

```bash
uv run kedro run --pipeline prod    # production
uv run kedro run --pipeline pprd    # pré-production
```

## Tests

Voir `src/tests/pipelines/share_data/test_nodes.py`.

