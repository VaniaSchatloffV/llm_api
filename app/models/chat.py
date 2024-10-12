from app.dependencies import get_settings

settings = get_settings()

import sqlalchemy as sal
from sqlalchemy.orm import registry
from sqlalchemy.sql import func
mapper_registry = registry()

Base = mapper_registry.generate_base()

class ConversationObject(Base):
    __tablename__ = 'conversations'
    __table_args__ = {'schema': settings.postgres_schema} 
    __attributes__ = [
            'id', 'user_id', 'name', 'qualified', 'created_at', 'finished_at'
        ]
    
    id                          = sal.Column('id', sal.BigInteger, primary_key=True, autoincrement=True)
    user_id                     = sal.Column('user_id', sal.BigInteger)
    name                        = sal.Column('name', sal.String(length=256))
    qualified                   = sal.Column('qualified', sal.Boolean, default=False)
    created_at                  = sal.Column('created_at', sal.DateTime(timezone=True), server_default=func.now())
    finished_at                 = sal.Column('finished_at', sal.DateTime(timezone=True))
    
    def __repr__(self):
        return(f"ConversationObject (id={self.id}, user_id={self.user_id}, name={self.name}, created_at={self.created_at}, finished_at={self.finished_at})")
    
    def set_dictionary(self, data: dict):
        for attr in self.__attributes__:
            value = data.get(attr)
            if value is not None:
                setattr(self, attr, value)
    
    def get_dictionary(self):
        result = {}
        for attr in self.__attributes__:
            result[attr] = getattr(self, attr)
        return result


class MessagesObject(Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': settings.postgres_schema} 
    __attributes__ = [
            'id', 'conversation_id', 'message', 'type', 'created_at'
        ]
    
    id                          = sal.Column('id', sal.BigInteger, primary_key=True, autoincrement=True)
    conversation_id             = sal.Column('conversation_id', sal.BigInteger)
    message                     = sal.Column('message', sal.JSON())
    type                        = sal.Column('type', sal.String(50))
    created_at                  = sal.Column('created_at', sal.DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return(f"MessagesObject (id={self.id}, conversation_id={self.conversation_id}, message={self.message}, type={self.type}), created_at={self.created_at}")
    
    def set_dictionary(self, data: dict):
        for attr in self.__attributes__:
            value = data.get(attr)
            if value is not None:
                setattr(self, attr, value)
    
    def get_dictionary(self):
        result = {}
        for attr in self.__attributes__:
            result[attr] = getattr(self, attr)
        return result