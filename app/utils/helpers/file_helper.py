from app.dependencies import get_settings
from fastapi import HTTPException
from io import BytesIO
from datetime import datetime, timezone
from app.crud.DBORMHandler import DB_ORM_Handler

import pandas as pd
import os
import random
from sqlalchemy.orm import aliased
from sqlalchemy import and_, desc

from app.models.files import FileObject


# Todo lo relacionado a archivos

settings = get_settings()
OPTIONS = ["csv", "xlsx"]

def to_file(type: str, data: list):
    if type == "csv":
        return to_csv(data)
    if type == "xlsx":
        return to_excel(data)
    

def to_csv(data: list):
    """
    Almacena data en un archivo csv. Retorna id de archivo.
    """
    file_name = random.randint(0, 100000)
    file_path = settings.temp_files + str(file_name) + ".csv"
    df = pd.DataFrame(data)
    df.to_csv(file_path)
    return str(file_name)

def to_excel(data: list):
    """
    Almacena data en un archivo xlsx. Retorna id de archivo.
    """
    file_name = random.randint(0, 100000)
    file_path = settings.temp_files + str(file_name) + ".xlsx"
    df = pd.DataFrame(data)
    df.to_excel(file_path)
    return file_name




def get_file_path(file_id: int):
    """
    Retorna string con la ruta de archivo
    """
    with DB_ORM_Handler() as db:
        res = db.getObjects(
            FileObject,
            FileObject.id == file_id
        )
        if res:
            res = res.pop().get_dictionary()
            file_path = settings.temp_files + str(res.get("name")) + "." + str(res.get("extension"))
            file_path = os.path.abspath(file_path)
            return file_path
        else:
            raise HTTPException(status_code=404, detail="File not found")

def file_iterator(file_path: str):
    """
    Itera sobre archivo
    """
    if "csv" in file_path or "png" in file_path:
        with open(file_path, mode="rb") as file:
            yield from file
    elif "xlsx" in file_path:
        with open(file_path, "rb") as excel_file:
            while chunk := excel_file.read(8192):  # 8 KB
                yield chunk

def download_file(file_id: int) -> BytesIO:
    """
    Descarga archivo por chunks
    """
    file_path = get_file_path(file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return file_iterator(file_path)

def csv_to_excel(user_id: int, conversation_id: int, file_id_csv: int):
    with DB_ORM_Handler() as db:
        subquery = db.session.query(FileObject.name).filter(FileObject.id == file_id_csv).subquery()

        existence = db.getObjects(
            FileObject,
            FileObject.name == subquery.c.name,
            FileObject.extension == 'xlsx',
            columns=[FileObject.id]
        )
        if existence:
            return existence.pop().get("id")
    file_path = get_file_path(file_id_csv)
    read_file_product = pd.read_csv(file_path)
    excel_file_path = file_path.replace(".csv", ".xlsx")
    read_file_product.to_excel(excel_file_path, index=None, header=True)
    name = os.path.splitext(os.path.basename(file_path))[0]
    file_id = new_file(user_id=user_id, conversation_id=conversation_id, name=name, extension="xlsx")
    return file_id

def file_exists(file_id: str):
    with DB_ORM_Handler() as db:
        count = db.countObjects(
            FileObject,
            FileObject.id == file_id,
            FileObject.deleted_at == None
        )
    if count == 0:
        return False
    return True

def new_file(user_id: int, conversation_id: int, name: str, extension: str):
    """
    Función para crear un nuevo archivo en la bd. 
    Retorna el id del archivo
    """
    with DB_ORM_Handler() as db:
        File = FileObject()
        File.user_id = user_id
        File.conversation_id = conversation_id
        File.name = name
        File.extension = extension
        File_id = db.saveObject(p_obj=File, get_obj_attr=True, get_obj_attr_name="id")
        return File_id
    
def get_last_file_from_conversation(conversation_id):
    with DB_ORM_Handler() as db:
        files = db.getObjects(
            FileObject,
            FileObject.conversation_id == conversation_id,
            FileObject.extension.in_(['csv', 'xlsx']),
            order_by= [desc(FileObject.id)],
            limit = 1    
        )
    return files

def delete_file(file_id: int):
    filepath = get_file_path(file_id)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def search_expired_files_and_delete():
    with DB_ORM_Handler() as db:
        files = db.getObjects(
            FileObject,
            FileObject.expires_at <= datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            FileObject.deleted_at == None,
            columns=[FileObject.id]
        )
        for file in files:
            if delete_file(file.get("id")):
                db.updateObjects(
                    FileObject,
                    FileObject.id == file.get("id"),
                    deleted_at=datetime.now(timezone.utc)
                )

    
