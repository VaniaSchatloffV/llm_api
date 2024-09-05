from configs.config import get_settings

settings = get_settings()

import sqlalchemy as sal
from sqlalchemy.orm import registry
from sqlalchemy.sql import func
mapper_registry = registry()

Base = mapper_registry.generate_base()

class MessagesObject(Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': settings.postgres_schema} 
    __attributes__ = [
            'id', 'conversation_id', 'message', 'type', 'created_at'
        ]
    
    id                          = sal.Column('id', sal.BigInteger, primary_key=True, autoincrement=True)
    conversation_id             = sal.Column('conversation_id', sal.BigInteger)
    message                     = sal.Column('name', sal.JSON())
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