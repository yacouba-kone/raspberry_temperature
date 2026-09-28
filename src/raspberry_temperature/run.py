
"""Application entry point.

Point d'entrée du projet une fois empaqueté (`kedro package`) : expose la
classe `ProjectContext` et la fonction `run_package()` appelée par la commande
`python -m raspberry_temperature.run`.
"""
from pathlib import Path
from typing import Dict

from kedro.framework.context import KedroContext, load_package_context
from kedro.pipeline import Pipeline

#from raspberry_temperature.pipeline import create_pipelines
# NB : `pipeline_registry` expose `register_pipelines()`, pas
# `create_pipelines()`. Cet import lèvera donc une `ImportError` ; il faudra
# écrire `from raspberry_temperature.pipeline_registry import register_pipelines`
# (ou rétablir `create_pipelines`) pour que ce module soit exécutable.
from raspberry_temperature.pipeline_registry import create_pipelines

class ProjectContext(KedroContext):
    """Users can override the remaining methods from the parent class here,
    or create new ones (e.g. as required by plugins)
    """

    # Métadonnées du projet, telles que générées par le template Kedro
    project_name = "raspberry-temperature"
    # `project_version` is the version of kedro used to generate the project
    project_version = "0.16.3"
    package_name = "raspberry_temperature"

    def _get_pipelines(self) -> Dict[str, Pipeline]:
        """Retourne les pipelines à exécuter pour ce contexte projet."""
        return create_pipelines()


def run_package():
    """Charge le contexte du projet Kedro puis exécute le pipeline par défaut."""
    # Entry point for running a Kedro project packaged with `kedro package`
    # using `python -m <project_package>.run` command.
    # `load_package_context` reconstruit le contexte Kedro (catalogue,
    # paramètres, pipelines, credentials) à partir du répertoire courant
    project_context = load_package_context(
        project_path=Path.cwd(), package_name=Path(__file__).resolve().parent.name
    )
    project_context.run()


if __name__ == "__main__":
    # Exécution directe : `python -m raspberry_temperature.run`
    run_package()