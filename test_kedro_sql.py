from sqlalchemy import create_engine, text

connection_string = (
    "mssql+pyodbc://@raspberry-sql.database.windows.net/"
    "raspberry-temperature"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&Encrypt=yes"
    "&Authentication=ActiveDirectoryDefault"
)

engine = create_engine(connection_string)

with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print("Connexion Azure SQL OK :", result.scalar())