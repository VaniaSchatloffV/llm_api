from fastapi_utilities import repeat_at
from app.crud.DBORMHandler import DB_ORM_Handler

@repeat_at(cron="* * * * *")
def delete_expired():
    query = """DELETE FROM archivos 
            WHERE expires_at < NOW();
            """
    with DB_ORM_Handler() as db:
        db.query(query)

    return