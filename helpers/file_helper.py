import pandas as pd
import os
import random

def to_csv(data: list):
    file_id = random.randint(0, 100000)
    file_path = os.getenv("TEMP_FILES") + "/" + str(file_id) + ".csv"
    df = pd.DataFrame(data)
    df.to_csv(file_path)
    return file_id

def to_excel(data: list):
    file_id = random.randint(0, 100000)
    file_path = os.getenv("TEMP_FILES") + "/" + str(file_id) + ".xlsx"
    df = pd.DataFrame(data)
    df.to_excel(file_path)
    return file_id

def get_file_csv_name(file_id: int):
    file_path = os.getenv("TEMP_FILES") + "/" +  str(file_id) + ".csv"
    return file_path

def get_file_xlsx_name(file_id: int):
    file_path = os.getenv("TEMP_FILES") + "/" +  str(file_id) + ".xlsx"
    return file_path

def delete_file(file_id: int, file_type: str):
    if file_type == "csv":
        file_path = get_file_csv_name