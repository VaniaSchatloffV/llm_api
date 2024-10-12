from app.dependencies import get_settings
from app.models.chat import ConversationObject 

settings = get_settings()

import sqlalchemy as sal
from sqlalchemy.orm import registry
from sqlalchemy.sql import func
from datetime import timedelta

mapper_registry = registry()

Base = mapper_registry.generate_base()

class MetricObject(Base):
    __tablename__ = 'metrics'
    __table_args__ = {'schema': settings.postgres_schema} 
    __attributes__ = [
            'id', 'conversation_id' ,'calification', 'data', 'metrics', 'created_at'
        ]
    
    id                          = sal.Column('id', sal.BigInteger, primary_key=True, autoincrement=True)
    conversation_id             = sal.Column('conversation_id', sal.BigInteger, sal.ForeignKey(ConversationObject.id))
    data                        = sal.Column('data', sal.JSON())
    calification                = sal.Column('calification', sal.INTEGER())
    metrics                     = sal.Column('metrics', sal.JSON())
    created_at                  = sal.Column('created_at', sal.DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return(f"MetricObject (id={self.id}, conversation_id={self.conversation_id})")
    
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