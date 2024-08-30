# DB_ORM_Handler
from configs.config import get_settings

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
    pass

class DB_ORM_Handler(object):

    def __init__(self, conn_str: Optional[str] = CONN):
        try:
            self.engine = sal.create_engine(conn_str, pool_reset_on_return=None,
    isolation_level="AUTOCOMMIT",pool_pre_ping=True, pool_recycle=300, poolclass=NullPool )
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
            return False
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
            except Exception as e:
                print(e)
                return False
            return True

        return True

    def query(self, query):
        """
        Ejecuta querys en texto
        """
        try:
            statement = text(query)
            rs = self.session.execute(statement)
            return rs

        except Exception as e:
            raise e

    def getObjects(self, p_obj, *args, defer_cols=[], order_by=None, **kwargs):
        
        @timeout(5.0)
        def execute_query():
            sess = self.session()
            rs = None
            error = False
            exception = None

            for retry in range(0, 10):
                try:
                    query = sess.query(p_obj)

                    # Apply filters if any
                    if len(kwargs) > 0 or len(args) > 0:
                        query = query.filter_by(**kwargs) if len(kwargs) > 0 else query.filter(*args)

                    # Apply deferred columns if any
                    if len(defer_cols) > 0:
                        defer_lst = list([defer(x) for x in defer_cols])
                        query = query.options(*defer_lst)

                    # Apply order_by if provided
                    if order_by:
                        query = query.order_by(*order_by)

                    rs = query.all()
                    error = False

                except Exception as e:
                    error = True
                    exception = e
                    time.sleep(5)
                finally:
                    self.session.remove()
                    self.session.close()

                if not error:
                    break

            if error:
                raise exception

            return rs

        try:
            return execute_query()
        except Exception as e:
            print("***** TIMEOUT *****", e)
            return None

        
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
                    print("Duplicate entry: Trying merge")
                    if p_objs is not None:
                        for obj in p_objs:
                            sess.merge(obj)
                    if p_obj is not None:
                        sess.merge(p_obj)
                    sess.commit()
                    done = True
                except Exception as e:
                    error = e
                    time.sleep(5)
            
            if not done:
                raise RuntimeError("No se pudo almacenar en DB: ", error)

        except Exception as e:
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