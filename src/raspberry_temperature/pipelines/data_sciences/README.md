# Pipeline : data sciences

Entraînement du modèle de régression linéaire qui prédit la température du
Raspberry Pi, avec suivi des expériences dans MLflow.

## Rôle

Ce pipeline découpe les données nettoyées, entraîne le modèle (avec recherche
d'hyperparamètre), évalue ses performances et écrit ses prédictions.

## Nœuds (`nodes.py`)

| Nœud | Entrées | Sorties | Description |
| --- | --- | --- | --- |
| `split_data` | `cleaned_data`, `params:features`, `params:label_name` | `x_train`, `x_test`, `y_train`, `y_test` | Découpage aléatoire entraînement / test (`test_size=0.2`, `random_state=42` par défaut) |
| `train_model` | `x_train`, `x_test`, `y_train`, `y_test` | `model_temperature` | Recherche du meilleur `fit_intercept` (validation croisée à 5 folds), entraînement, évaluation et journalisation MLflow |
| `predict` | `model_temperature`, `x_test`, `y_test` | `output_table_dev` | DataFrame des valeurs réelles, des prédictions et d'un horodatage `Time` |
| `make_scatter` | - | figure matplotlib (`plot.png`) | Utilitaire d'analyse, non branché dans le pipeline |

## Pipeline (`pipeline.py`)

`create_training_pipeline()`, taggé `ds_training_tag` et enregistré sous la clé
`training` du registre des pipelines.

## Paramètres

Définis dans `conf/base/parameters.yml` :
`features` (`intensity`, `humidity`, `ratio`), `label_name` (`temperature`),
`test_size`, `random_state`.

## Suivi MLflow

- serveur de suivi : `http://127.0.0.1:5000`, expérience `raspberry-temperature`
- paramètres journalisés : `model_type`, `best_fit_intercept`
- métriques journalisées : `r2_score`, `rmse`, `mse`, `explained_variance`
- artefacts : `plots/residual_analysis.png`, `plots/actual_vs_predicted.png` et
  le modèle `model`

## Exécution

```bash
uv run kedro run --pipeline training
```

## Tests

Voir `src/tests/pipelines/data_sciences/test_nodes.py`.

