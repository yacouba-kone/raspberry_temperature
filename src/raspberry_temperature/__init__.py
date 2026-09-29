"""Package Python du projet Kedro `raspberry-temperature`.

Ce fichier marque le dossier `src/raspberry_temperature` comme un package
importable. Il ne contient volontairement aucun code : la logique est répartie
dans les sous-modules suivants :

    - ``azure_sql.py``         : connexion authentifiée (token Entra ID) à
                                 Azure SQL Database ;
    - ``pipeline_registry.py`` : enregistrement des pipelines auprès de Kedro ;
    - ``run.py``               : point d'entrée de l'applicatif empaqueté ;
    - ``datasets/``            : datasets Kedro personnalisés ;
    - ``pipelines/``           : les pipelines du projet (data engineering,
                                 data sciences et share data).

Remarque : le script déclaré dans `pyproject.toml`
(``raspberry-temperature = "raspberry_temperature:main"``) n'est pas défini
ici, ce qui rend la commande installée inopérante en l'état.
"""

