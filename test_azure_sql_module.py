from sqlalchemy import text

from raspberry_temperature.azure_sql import create_azure_sql_engine


engine = create_azure_sql_engine()

with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print("Connexion Azure SQL via module OK :", result.scalar())
