# DB_ORM_Handler

import time
from typing import Optional
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
import random

def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator

class TableDoesNotExist(Exception):
    pass

class DB_ORM_Handler(object):

    def __init__(self, conn_str):
        try:
            print("DB_ORM_Handler:init %s" % conn_str)
            self.engine = sal.create_engine(conn_str, connect_args={'timeout': 60}, pool_reset_on_return=None,
    isolation_level="AUTOCOMMIT",pool_pre_ping=True, pool_recycle=300, poolclass=NullPool )
        except Exception as e:
            raise e

        session_factory = sessionmaker(self.engine,expire_on_commit=False,autocommit=False, autoflush=False )
        self.session = scoped_session(session_factory)

    # def __del__(self):
    #     print("DB_ORM_Handler:closing engine")
    #     self.engine.dispose()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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
            metadata = sal.MetaData(engine)
            table = sal.Table(table_name, metadata, autoload=True, autoload_with=engine)

            return table
        raise TableDoesNotExist(table_name)

    def initialize(self, p_object):
        if not self.existTable(p_object.__tablename__):
            engine = self.getEngine()
            try:
                # Implement the creation
                p_object.metadata.create_all(engine)
            except Exception as e:
                print(e)
                return False
            return True

        return True

    def query(self, query):
        print("DB_ORM_Handler:query %s" % query)
        try:
            statement = text(query)
            rs = self.session.execute(statement)
            print("DB_ORM_Handler:query %s" % rs)
            return rs

        except Exception as e:
            print("error in query: %s" % query)
            raise e

    def getObjects(self, p_obj, *args, defer_cols=[], **kwargs):
        print("DB_ORM_Handler:getObjects %s args %s kw_args %s" % (type(p_obj).__name__,args, kwargs))
        
        @timeout(5.0)
        def execute_query():
            sess = self.session()
            rs = None
            error = False
            exception = None
            
            # force random failure
            fail = random.randint(0,100)
            if fail==0:
                print("getObjects ********** ARTIFICIAL FAILURE ************** ")
                time.sleep(10)
            
            for retry in range(0,10):
                print("DB_ORM_Handler:getObjects retry %d" % retry)
                try:
                    if len(kwargs)>0 or len(args)>0:
                        if len(defer_cols)>0:
                            defer_lst = list([defer(x) for x in defer_cols])
                            if len(kwargs)>0:
                                print("DB_ORM_Handler:getObjects defered kwargs %s" % kwargs)
                                rs = sess.query(p_obj).filter_by(**kwargs).options(*defer_lst).all()
                            else:
                                print("DB_ORM_Handler:getObjects defered args %s" % args)
                                rs = sess.query(p_obj).filter(*args).options(*defer_lst).all()
                        else:
                            if len(kwargs)>0:
                                print("DB_ORM_Handler:getObjects kwargs %s" % kwargs)

                                query = Query([p_obj]).filter_by(**kwargs)
                                rs = query.with_session(sess).all()

                                #rs = sess.query(p_obj).filter_by(**kwargs).all()
                                #print("DB_ORM_Handler:getObjects kwargs rs" % rs)

                            else:
                                print("DB_ORM_Handler:getObjects args %s" % args)
                                rs = sess.query(p_obj).filter(*args).all()
                    else:
                        if len(defer_cols)>0:
                            print("DB_ORM_Handler:getObjects noargs %s" % defer_lst)
                            defer_lst = list([defer(x) for x in defer_cols])
                            rs = sess.query(p_obj).options(*defer_lst).all()
                        else:
                            print("DB_ORM_Handler:getObjects all")
                            rs = sess.query(p_obj).all()

                    error = False

                    #print("DB_ORM_Handler:getObjects rs %s" % rs)
                except Exception as e:
                    print("DatabaseError:",e)
                    error = True
                    exception = e
                    time.sleep(5)
                finally:
                    if len(defer_cols)==0:
                        self.session.remove()
                        self.session.close()

                break

            if error:
                raise exception

            print("DB_ORM_Handler:getObjects return rs %s" % rs)
            return rs

        try:
            return execute_query()
        except Exception as e:
            print("***** TIMEOUT *****",e)
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

    def saveObject(self, p_obj, get_obj_attr: Optional[bool] = False, get_obj_attr_name: Optional[bool] = "id"):
        print("DB_ORM_Handler:saveObject %s" % (type(p_obj).__name__))
        sess = self.session()
        try:
            sess.add(p_obj)
            e = None
            done=False
            for r in range(0,10):
                try:
                    sess.commit()
                    done=True
                    break
                except Exception as e:
                    print("retry commit",e)
                    time.sleep(5)
            if not done:
                raise RuntimeError("could not save object to database:",e)

        except Exception as e:
            raise e
        finally:
            self.session.remove()

        print("DB_ORM_Handler:saveObject done %s" % (type(p_obj).__name__))
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