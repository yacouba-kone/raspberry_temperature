"""
Fonctions utilitaires d'accès à Azure SQL Database.

Ce module centralise la création d'un moteur SQLAlchemy authentifié auprès de
Microsoft Entra ID, sans login ni mot de passe. Il est utilisé par le dataset
Kedro `raspberry_temperature.datasets.azure_sql_dataset`.
"""

import struct

from azure.identity import DefaultAzureCredential
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL


# Coordonnées du serveur Azure SQL cible
SERVER = "raspberry-sql.database.windows.net"
DATABASE = "raspberry-temperature"


def create_azure_sql_engine():
    """Crée un moteur SQLAlchemy connecté à Azure SQL Database.

    L'authentification s'appuie sur `DefaultAzureCredential` : un token
    Microsoft Entra ID est récupéré puis transmis à pyodbc, ce qui évite de
    stocker des identifiants dans le code ou dans les fichiers de configuration.

    Returns:
        Engine: moteur SQLAlchemy de type ``mssql+pyodbc`` prêt à l'emploi.
    """
    # `DefaultAzureCredential` essaie successivement plusieurs sources
    # (variables d'environnement, identité managée, Azure CLI, ...)
    credential = DefaultAzureCredential()

    # Token d'authentification pour la ressource Azure SQL Database
    # (`.default` demande les permissions par défaut de la ressource)
    token = credential.get_token(
        "https://database.windows.net/.default"
    )

    # pyodbc attend un token encodé en UTF-16 Little Endian
    token_bytes = token.token.encode("utf-16-le")

    # Structure attendue par SQL Server : taille du token (4 octets) + token
    access_token = struct.pack(
        f"<I{len(token_bytes)}s",
        len(token_bytes),
        token_bytes,
    )

    # URL SQLAlchemy SANS identifiants : l'authentification se fait
    # uniquement via le token Entra ID placé dans `connect_args`
    connection_url = URL.create(
        "mssql+pyodbc",
        host=SERVER,
        database=DATABASE,
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "Encrypt": "yes",
        },
    )

    # Le token est fourni à pyodbc via l'attribut ODBC 1256
    # (SQL_COPT_SS_ACCESS_TOKEN) avant l'ouverture de la connexion
    engine = create_engine(
        connection_url,
        connect_args={
            "attrs_before": {
                1256: access_token,
            }
        },
    )

    # SQLAlchemy peut ajouter automatiquement l'option
    # « Trusted_Connection=Yes », incompatible avec un token d'accès :
    # ce hook la retire de la chaîne de connexion à chaque `do_connect`
    @event.listens_for(engine, "do_connect")
    def remove_trusted_connection(
        dialect,
        conn_rec,
        cargs,
        cparams,
    ):
        cargs[0] = cargs[0].replace(
            ";Trusted_Connection=Yes",
            "",
        )

    return engine