# Tests : pipeline data sciences

Tests unitaires des nœuds du pipeline d'entraînement
(`src/raspberry_temperature/pipelines/data_sciences/nodes.py`).

| Test | Vérifie |
| --- | --- |
| `test_split_data` | pour 10 observations et `test_size=0.3` : 7 lignes d'entraînement, 3 lignes de test, colonnes `feature` et `label` conservées |

Le faux modèle `Model_couple_test` (défini dans le fichier de test) surcharge
`predict` pour retourner la somme de la première ligne : il permet de tester le
nœud `predict` sans entraîner de vrai modèle.

Une ancienne version du test, écrite pour une API différente de `split_data`
(retour sous forme de liste), reste commentée en fin de fichier.

## Exécution

```bash
uv run pytest src/tests/pipelines/data_sciences -q
```

