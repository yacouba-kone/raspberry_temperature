from sqlalchemy import text

from raspberry_temperature.azure_sql import create_azure_sql_engine

engine = create_azure_sql_engine()

with engine.connect() as connection:
    rows = connection.execute(
        text("""
            SELECT TOP 10
                y_pred,
                [Time]
            FROM dbo.training_table_prod
            ORDER BY [Time] DESC
        """)
    ).fetchall()

    for row in rows:
        print(row)
