# DB_ORM_Handler
from app.dependencies import get_settings
from app.logger import LOGGER

import time
from typing import Optional, Type
import sqlalchemy as sal
from sqlalchemy import create_engine, and_
from sqlalchemy.sql import func
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import defer
from sqlalchemy.orm import undefer
from sqlalchemy.orm import Query
from sqlalchemy.pool import NullPool


import multiprocessing.pool
import functools
import pymysql
import random

settings = get_settings()

# Datos de conexión a la base de datos PostgreSQL
db_host = settings.postgres_host
db_port = settings.postgres_port
db_name = settings.postgres_db
db_user = settings.postgres_user
db_password = settings.postgres_password

CONN = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator

class TableDoesNotExist(Exception):
    LOGGER.error("Tabla no existe")
    pass

class DB_ORM_Handler(object):

    def __init__(self, conn_str: Optional[str] = CONN):
        try:
            self.engine = sal.create_engine(conn_str, pool_reset_on_return=None,
    isolation_level="AUTOCOMMIT",pool_pre_ping=True, pool_recycle=300, poolclass=NullPool )
            LOGGER.debug(f"Creando instancia DB_ORM_Handler: {conn_str}")
        except Exception as e:
            raise e

        session_factory = sessionmaker(self.engine,expire_on_commit=False,autocommit=False, autoflush=False )
        self.session = scoped_session(session_factory)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.engine.dispose()

    def __del__(self):
        self.engine.dispose()

    def getEngine(self):
        return self.engine

    def existTable(self,table_name):
        engine = self.getEngine()
        ins = sal.inspect(engine)
        if not ins.has_table(table_name):
            LOGGER.debug(f"Tabla {table_name} no existe")
            return False
        LOGGER.debug(f"Tabla {table_name} existe")
        return True

    def getTable(self,table_name):
        if self.existTable(table_name):
            engine = self.getEngine()
            metadata = sal.MetaData()
            table = sal.Table(table_name, metadata, autoload_with=engine)
            return table
        raise TableDoesNotExist(table_name)

    def createTable(self, p_object):
        """
        Crea tablas
        """
        if not self.existTable(p_object.__tablename__):
            engine = self.getEngine()
            try:
                p_object.metadata.create_all(engine)
                LOGGER.debug(f"Tabla {p_object.__tablename__} creada con éxito")
            except Exception as e:
                LOGGER.error(f"DB_ORM_HANDLER: Tabla {p_object.__tablename__} no ha podido ser creada. ERROR : {e}")
                return False
            return True

        return True

    def query(self, query, return_data: Optional[bool] = False):
        """
        Ejecuta queries en texto y retorna los resultados como diccionarios si se especifica.
        """
        try:
            statement = text(query)
            LOGGER.debug(f"Ejecutando query: {statement}")
            rs = self.session.execute(statement)
            if return_data:
                # Obtener nombres de columnas
                keys = rs.keys()
                # Convertir cada fila en un diccionario
                return [dict(zip(keys, row)) for row in rs.fetchall()]
            return rs

        except Exception as e:
            LOGGER.error(f"DB_ORM_HANDLER: Error al ejecutar consulta. ERROR = {e}")
            raise e


    def getObjects(self, p_obj, *args, defer_cols=[], columns: Optional[list] = None, order_by: Optional[list] = None, limit: Optional[int] = None, offset: Optional[int] = None, join_conditions: Optional[list] = None, **kwargs):
    
        sess = self.session()
        
        # Inicia la consulta, con columnas si están especificadas
        query = sess.query(*columns) if columns else sess.query(p_obj)
        
        # Aplica las condiciones de JOIN si se especifican
        if join_conditions:
            for join_cond in join_conditions:
                query = query.join(*join_cond)
        
        # Aplica filtros
        if args:
            query = query.filter(*args)
        if kwargs:
            query = query.filter_by(**kwargs)

        # Ordenar por columnas si se especifica
        if order_by:
            query = query.order_by(*order_by)

        # Deferir columnas si es necesario
        if defer_cols:
            for col in defer_cols:
                query = query.options(defer(col))

        # Aplica límite si se especifica
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)

        try:
            results = query.all()
            
            if columns:
                # Convierte las tuplas a diccionarios u objetos personalizados
                results = [dict(zip([col.key for col in columns], row)) for row in results]
            return results

        except Exception as e:
            LOGGER.error(f"DB_ORM_HANDLER: Error al obtener objetos. ERROR = {e}")
            raise e
        finally:
            self.session.remove()



        
    def refreshObject(self, p_obj):
        sess = self.session()
        try:
            sess.expire(p_obj)
            sess.refresh(p_obj)
        except Exception as e:
            raise e
        finally:
            self.session.remove()

        return True

    def commit(self):
        sess = self.session()
        try:
            sess.commit()
        except Exception as e:
            raise e
        finally:
            self.session.remove()
        return True

    def updateObjects(self, p_obj, *args, **kw_args):
        sess = self.session()
        try:
            rs = sess.query(p_obj).filter(*args).update(kw_args)
            sess.commit()
            LOGGER.debug(f"{rs} objetos actualizados")
        except Exception as e:
            raise e
        finally:
            self.session.remove()

        return rs

    def saveObject(self, p_obj: Optional[Type] = None, p_objs: Optional[list] = None, integrity_merge: Optional[bool] = True, get_obj_attr: Optional[bool] = False, get_obj_attr_name: Optional[bool] = "id"):
        """
        Almacena objetos en base de datos:
         - p_obj: Opcional. Objeto a almacenar
         - p_objs: Opcional. Lista de objetos a almacenar
         - integrity_merge: Opcional. True si se desea upsert, False si no. Por defecto True.
         
        """
        if p_obj is None and p_objs is None:
            return False
        error = None
        sess = self.session()
        try:
            if p_obj is not None:
                sess.add(p_obj)
            elif p_objs is not None:
                sess.add_all(p_objs)
            done = False
            for _ in range(10):
                try:
                    sess.commit()
                    done = True
                    break
                except sal.exc.IntegrityError as dbapi:
                    # Error de integridad
                    sess.rollback()
                    if not integrity_merge:
                        raise
                    if p_objs is not None:
                        for obj in p_objs:
                            sess.merge(obj)
                    if p_obj is not None:
                        sess.merge(p_obj)
                    sess.commit()
                    done = True
                except Exception as e:
                    sess.rollback()
                    error = e
                    time.sleep(5)
            
            if not done:
                raise RuntimeError("No se pudo almacenar en DB: ", error)

        except Exception as e:
            LOGGER.error(f"DB_ORM_HANDLER: Error al guardar objetos. ERROR = {e}")
            if sess:
                sess.rollback()
            raise e
        finally:
            self.session.remove()
        if get_obj_attr:
            obj_id = getattr(p_obj, 'id', None)
            return obj_id
        return True

    def destroyObject(self, p_obj):
        sess = self.session()
        try:
            sess.delete(p_obj)
            sess.commit()
        except Exception as e:
            raise e
        finally:
            self.session.remove()

        return True
    
    def countObjects(self, p_obj, *args, **kwargs):
        """
        Cuenta los registros en la tabla especificada, con filtros opcionales.
        
        :param p_obj: El modelo de la tabla (ORM class).
        :param args: Filtros opcionales (e.g. p_obj.id == 5).
        :param kwargs: Filtros adicionales como clave-valor.
        :return: El número de registros.
        """
        sess = self.session()
        try:
            query = sess.query(func.count()).select_from(p_obj)
            if args:
                query = query.filter(*args)
            if kwargs:
                query = query.filter_by(**kwargs)

            result = query.scalar()
            return result

        except Exception as e:
            LOGGER.error(f"DB_ORM_HANDLER: Error al ejecutar consulta COUNT. ERROR = {e}")
            raise e
        finally:
            self.session.remove()
    
    def destroyObjects(self, p_obj, *args, **kwargs):
        """
        Elimina registros de la tabla basada en las condiciones especificadas.
        
        :param p_obj: El modelo de la tabla (ORM class).
        :param args: Condiciones en formato de argumentos posicionales.
        :param kwargs: Condiciones adicionales en formato de clave-valor.
        """
        sess = self.session()
        try:
            query = sess.query(p_obj).filter(*args)
            
            if kwargs:
                query = query.filter_by(**kwargs)
            
            rows_deleted = query.delete(synchronize_session=False)
            sess.commit()
            return rows_deleted

        except Exception as e:
            LOGGER.error(f"DB_ORM_HANDLER: Error al eliminar objetos. ERROR = {e}")
            sess.rollback()
            raise e
        finally:
            self.session.remove()
