"""
Script utilitaire de création de la table Azure SQL `dbo.training_table_prod`.

Ce script est lancé manuellement, en dehors de Kedro, pour préparer la table
qui reçoit les prédictions de production (dataset `output_table_prod` du
catalogue Kedro).

Il est idempotent : la table n'est créée que si elle n'existe pas déjà, donc il
peut être relancé sans risque.
"""

import struct

from azure.identity import AzureCliCredential
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import URL


# Coordonnées du serveur Azure SQL cible
SERVER = "raspberry-sql.database.windows.net"
DATABASE = "raspberry-temperature"


# Récupération du token Microsoft Entra ID
# `AzureCliCredential` réutilise la session Azure CLI déjà ouverte
# (obtenue au préalable avec la commande `az login`)
credential = AzureCliCredential()

# Token d'authentification pour la ressource Azure SQL Database
token = credential.get_token(
    "https://database.windows.net/.default"
)

# pyodbc attend un token encodé en UTF-16 Little Endian
token_bytes = token.token.encode("utf-16-le")

# Structure attendue par SQL Server : taille du token (4 octets) suivie du token
access_token = struct.pack(
    f"<I{len(token_bytes)}s",
    len(token_bytes),
    token_bytes,
)


# URL SQLAlchemy SANS Authentication
# Aucun identifiant n'est renseigné ici : l'authentification se fait
# uniquement avec le token Entra ID passé plus bas dans `connect_args`
connection_url = URL.create(
    "mssql+pyodbc",
    host=SERVER,
    database=DATABASE,
    query={
        "driver": "ODBC Driver 18 for SQL Server",
        "Encrypt": "yes",
    },
)


# Moteur SQLAlchemy : le token est transmis à pyodbc via l'attribut ODBC 1256
# (SQL_COPT_SS_ACCESS_TOKEN) au moment de l'ouverture de la connexion
engine = create_engine(
    connection_url,
    connect_args={
        "attrs_before": {
            1256: access_token,
        }
    },
)


# SQLAlchemy peut ajouter automatiquement cette option.
# Elle est incompatible avec l'access token.
@event.listens_for(engine, "do_connect")
def remove_trusted_connection(
    dialect,
    conn_rec,
    cargs,
    cparams,
):
    # Supprime « Trusted_Connection=Yes » de la chaîne de connexion ODBC
    # générée par SQLAlchemy : cette option est incompatible avec le token
    cargs[0] = cargs[0].replace(
        ";Trusted_Connection=Yes",
        "",
    )


# Bloc principal : création de la table de destination des prédictions
with engine.begin() as connection:

    # `IF OBJECT_ID(...) IS NULL` évite une erreur si la table existe déjà
    connection.execute(
        text(
            """
            IF OBJECT_ID('dbo.training_table_prod', 'U') IS NULL
            BEGIN
                CREATE TABLE dbo.training_table_prod (
                    y_pred FLOAT NULL,
                    [Time] VARCHAR(50) NULL
                );
            END
            """
        )
    )


# Message de confirmation affiché en fin de script
print("Table training_table_prod OK")