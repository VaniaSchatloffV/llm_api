import sqlalchemy as sal
from sqlalchemy.orm import registry
from sqlalchemy.sql import func
mapper_registry = registry()

Base = mapper_registry.generate_base()

class ConversationObject(Base):
    __tablename__ = 'conversations'
    __attributes__ = [
            'id', 'user_od', 'name', 'created_at', 'finished_at'
        ]
    
    id                          = sal.Column('id', sal.BigInteger, primary_key=True, autoincrement=True)
    user_id                     = sal.Column('user_id', sal.BigInteger)
    name                        = sal.Column('name', sal.String(length=256))
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