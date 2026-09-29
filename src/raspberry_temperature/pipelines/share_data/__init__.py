# Fonction de démonstration générée par le template Kedro.
# À noter : `pyproject.toml` déclare le script
# `raspberry-temperature = "raspberry_temperature:main"`, alors que ce `main`
# se trouve dans ce package (`...pipelines.share_data`) : le point d'entrée
# installé ne pointe donc pas vers ce code.
def main() -> None:
    """Affiche un simple message de bienvenue (sert de vérification rapide)."""
    print("Hello from raspberry-temperature!")
