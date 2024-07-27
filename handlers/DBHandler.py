from typing import Optional
import psycopg2
import os

# Datos de conexión a la base de datos PostgreSQL
db_host = os.getenv("POSTGRES_HOST")
db_port = os.getenv("POSTGRES_PORT")
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")


class DBHandler():
    def __init__(
            self,
            host: Optional[str] = db_host,
            port: Optional[str] = db_port,
            db_name: Optional[str] = db_name,
            db_user: Optional[str] = db_user,
            db_password: Optional[str] = db_password) -> None:
        self.set_connection(host, port, db_name, db_user, db_password)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def set_connection(
            self,
            host: Optional[str] = db_host,
            port: Optional[str] = db_port,
            db_name: Optional[str] = db_name,
            db_user: Optional[str] = db_user,
            db_password: Optional[str] = db_password):
        self.connection = psycopg2.connect(
            host=host,
            port=port,
            database=db_name,
            user=db_user,
            password=db_password
    )
        
    def execute(self, query, params: Optional[tuple] = ()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        cursor.close()
    
    def select(self, query, params: Optional[tuple] = ()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def insert_get_id(self, query, params=()):
        """
        Inserta fila en tabla y retorna el ultimo id.
        La columna identificadora debe llamarse id.
        """
        cursor = self.connection.cursor()
        cursor.execute(query + " RETURNING id", params)
        self.connection.commit()
        id = cursor.fetchone()[0]
        cursor.close()
        return id
    
    def close(self):
        self.connection.close()