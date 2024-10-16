from app.dependencies import get_settings
from app.models.chat import ConversationObject 

settings = get_settings()

import sqlalchemy as sal
from sqlalchemy.orm import registry
from sqlalchemy.sql import func
from datetime import timedelta

mapper_registry = registry()

Base = mapper_registry.generate_base()

class TokenObject(Base):
    __tablename__ = 'tokens'
    __table_args__ = {'schema': settings.postgres_schema} 
    __attributes__ = [
            'conversation_id' ,'input_token_used', 'output_tokens_used', 'created_at'
        ]
    
    conversation_id             = sal.Column('conversation_id', sal.BigInteger, sal.ForeignKey(ConversationObject.id), primary_key=True)
    input_tokens_used           = sal.Column('input_tokens_used', sal.BigInteger(), default=0)
    output_tokens_used          = sal.Column('output_tokens_used', sal.BigInteger(), default=0)
    created_at                  = sal.Column('created_at', sal.DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return(f"TokenObject (conversation_id={self.conversation_id})")