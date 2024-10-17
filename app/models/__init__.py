from .chat import ConversationObject, MessagesObject
from .files import FileObject
from .metrics import MetricObject
from .tokens import TokenObject

from ..crud.DBORMHandler import DB_ORM_Handler

def initialize_models():
    with DB_ORM_Handler() as db:
        db.createTable(ConversationObject)
        db.createTable(MessagesObject)
        db.createTable(FileObject)
        db.createTable(MetricObject)
        db.createTable(TokenObject)