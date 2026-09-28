import struct

from azure.identity import DefaultAzureCredential
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL


SERVER = "raspberry-sql.database.windows.net"
DATABASE = "raspberry-temperature"


def create_azure_sql_engine():
    credential = DefaultAzureCredential()

    token = credential.get_token(
        "https://database.windows.net/.default"
    )

    token_bytes = token.token.encode("utf-16-le")

    access_token = struct.pack(
        f"<I{len(token_bytes)}s",
        len(token_bytes),
        token_bytes,
    )

    connection_url = URL.create(
        "mssql+pyodbc",
        host=SERVER,
        database=DATABASE,
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "Encrypt": "yes",
        },
    )

    engine = create_engine(
        connection_url,
        connect_args={
            "attrs_before": {
                1256: access_token,
            }
        },
    )

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