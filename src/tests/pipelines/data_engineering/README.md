# Tests : pipeline data engineering

Tests unitaires des nœuds `clean_data` et `clean_data_prod`
(`src/raspberry_temperature/pipelines/data_engineering/nodes.py`).

| Test | Vérifie |
| --- | --- |
| `test_log_running_time` | test de fumée : la suite de tests s'exécute |
| `test_clean_data` | conservation d'une mesure à 31 °C et création de la colonne `ratio` (66 / 66 = 1.0) |
| `test_clean_data_prod` | décodage d'un message IoT Azure, conversion de `EventProcessedUtcTime` en datetime UTC, sélection des colonnes attendues et calcul du `ratio` |

## Exécution

```bash
uv run pytest src/tests/pipelines/data_engineering -q
```

