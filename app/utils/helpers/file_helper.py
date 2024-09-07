from app.dependencies import get_settings
from fastapi import HTTPException
from io import BytesIO
from typing import Iterator

import pandas as pd
import os
import random

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
    return file_id

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