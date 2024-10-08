from app.dependencies import get_settings
from fastapi import HTTPException
from io import BytesIO
from typing import Iterator

import pandas as pd
import os
import random

import json
from datetime import datetime
from typing import Optional, Union
from app.crud.DBORMHandler import DB_ORM_Handler
from app.models.chat import ConversationObject, MessagesObject
from app.models.files import FileObject
from sqlalchemy import desc


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
    if "csv" in file_path: #revisar como cambiar esto para que sea más modular y menos duro
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

def csv_to_excel(user_id : int, conversation_id : int, file_id_csv : int):
    file_path = get_file_path(file_id_csv)
    read_file_product = pd.read_csv(file_path)
    read_file_product.to_excel(file_path.replace("csv", "xlsx"), index = None, header=True)
    name = file_path.split('\\').pop().split(".")[0]
    file_id = new_file(user_id = user_id, conversation_id = conversation_id, name = name, extension = "xlsx")
    return file_id

def file_exists(file_id: str):
    file_path = get_file_path(file_id)
    return os.path.isfile(file_path)

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
        db.createTable(File)
        File_id = db.saveObject(p_obj=File, get_obj_attr=True, get_obj_attr_name="id")
        return File_id

def update_file(file_id: int, extension: str):
    """
    Función para actualizar extensión de archivo.
    """
    with DB_ORM_Handler() as db:
        return db.updateObjects(
            FileObject,
            FileObject.id == file_id,
            extension = extension
        )
    
def get_last_file_from_conversation(conversation_id):
    with DB_ORM_Handler() as db:
        files = db.getObjects(
            FileObject,
            FileObject.conversation_id == conversation_id,
            order_by= [desc(FileObject.id)],
            limit = 1    
        )
    return files
