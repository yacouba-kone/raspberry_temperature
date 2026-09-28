# Tests : pipeline share data

Test unitaire du nœud `predict`
(`src/raspberry_temperature/pipelines/share_data/nodes.py`).

| Test | Vérifie |
| --- | --- |
| `test_predict` | que le nœud `predict` s'exécute sans erreur sur une observation (`humidity=61.0`, `intensity=44.0`, `ratio=0.7`) avec un faux modèle |

Le faux modèle `Model_couple_test` (défini dans le fichier de test) surcharge
`predict` pour retourner la somme de la première ligne.

> Remarque : ce test ne contient pas encore d'assertion, il vérifie uniquement
> l'absence d'exception. Il reste à compléter, par exemple en contrôlant que le
> DataFrame retourné contient bien les colonnes `y_pred` et `Time`.

## Exécution

```bash
uv run pytest src/tests/pipelines/share_data -q
```

