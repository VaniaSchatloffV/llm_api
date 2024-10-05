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
    file_id = random.randint(0, 100000)
    file_path = settings.temp_files + "/" + str(file_id) + ".csv"
    df = pd.DataFrame(data)
    df.to_csv(file_path)
    return str(file_id)

def to_excel(data: list):
    """
    Almacena data en un archivo xlsx. Retorna id de archivo.
    """
    file_id = random.randint(0, 100000)
    file_path = settings.temp_files + "/" + str(file_id) + ".xlsx"
    df = pd.DataFrame(data)
    df.to_excel(file_path)
    return file_id

def get_file_csv_name(file_id: int):
    """
    Retorna string con la ruta de archivo csv
    """
    file_path = settings.temp_files + "/" +  str(file_id) + ".csv"
    return file_path

def get_file_xlsx_name(file_id: int):
    """
    Retorna string con la ruta de archivo xlsx
    """
    file_path = settings.temp_files + "/" +  str(file_id) + ".xlsx"
    return file_path

def file_iterator(file_path: str):
    """
    Itera sobre archivo
    """
    with open(file_path, mode="rb") as file:
        yield from file
    os.remove(file_path)

def excel_iterator(file_path: str) -> Iterator[bytes]:
    """
    Itera sobre archivo excel
    """
    with open(file_path, "rb") as excel_file:
        while chunk := excel_file.read(8192):  # 8 KB
            yield chunk
    os.remove(file_path)


def download_csv_file(file_id: int):
    """
    Descarga archivo csv por chunks
    """
    file_path = get_file_csv_name(file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return file_iterator(file_path)

def download_xlsx_file(file_id: int) -> BytesIO:
    """
    Descarga archivo xlsx por chunks
    """
    file_path = get_file_xlsx_name(file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return excel_iterator(file_path)


def csv_to_excel(file_id: int):
    file_path = get_file_csv_name(file_id)
    read_file_product = pd.read_csv (file_path)
    read_file_product.to_excel (settings.temp_files + "/" + str(file_id) + ".xlsx", index = None, header=True)
    os.remove(file_path)
    return file_id

def file_exists(file_id: str, file_type: str):
    if file_type == "csv":
        file_path = get_file_csv_name(file_id)
    elif file_type == "xlsx":
        file_path = get_file_xlsx_name(file_id)
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

