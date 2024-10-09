from .chat import ConversationObject, MessagesObject
from .files import FileObject

from ..crud.DBORMHandler import DB_ORM_Handler

def initialize_models():
    with DB_ORM_Handler() as db:
        db.createTable(ConversationObject)
        db.createTable(MessagesObject)
        db.createTable(FileObject)