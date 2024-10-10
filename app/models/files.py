from app.dependencies import get_settings
from app.models.chat import ConversationObject 

settings = get_settings()

import sqlalchemy as sal
from sqlalchemy.orm import registry
from sqlalchemy.sql import func
from datetime import timedelta

mapper_registry = registry()

Base = mapper_registry.generate_base()

class FileObject(Base):
    __tablename__ = 'files'
    __table_args__ = {'schema': settings.postgres_schema} 
    __attributes__ = [
            'id', 'user_id','conversation_id' ,'name', 'created_at', 'expires_at', 'extension', 'deleted_at'
        ]
    
    id                          = sal.Column('id', sal.BigInteger, primary_key=True, autoincrement=True)
    user_id                     = sal.Column('user_id', sal.BigInteger)
    conversation_id             = sal.Column('conversation_id', sal.BigInteger, sal.ForeignKey(ConversationObject.id))
    name                        = sal.Column('name', sal.String(length=256))
    created_at                  = sal.Column('created_at', sal.DateTime(timezone=True), server_default=func.now())
    expires_at                  = sal.Column('expires_at', sal.DateTime(timezone=True), server_default=func.now()+timedelta(days=settings.file_expiration_time_delta)) # Potencialmente cambiar numero de días
    extension                   = sal.Column('extension', sal.String(length=4))
    deleted_at                  = sal.Column('deleted_at', sal.DateTime(timezone=True), default=None)
    
    def __repr__(self):
        return(f"FileObject (id={self.id}, user_id={self.user_id}, name={self.name}, created_at={self.created_at}, expires_at={self.expires_at}, extension={self.extension})")
    
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