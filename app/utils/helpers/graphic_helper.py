import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from app.dependencies import get_settings

settings = get_settings()

def generar_grafico(csv_path, data_dict: dict = {}):
    color = data_dict.get("color", "blue")
    titulo = data_dict.get("titulo", "Gráfico generado")
    x_col_name = data_dict.get("x_col_name", "Eje X")
    y_col_name = data_dict.get("y_col_name", "Eje Y")
    tipo_grafico = data_dict.get("tipo_grafico", "scatter")
    x_col = data_dict.get("x_col")
    y_col = data_dict.get("y_col")

    df = pd.read_csv(csv_path)
    plt.figure()

    if titulo:
        plt.title(titulo)

    if tipo_grafico == 'scatter':
        fig = sns.scatterplot(data=df, x=x_col, y=y_col, color=color)
    elif tipo_grafico == 'line':
        fig = sns.lineplot(data=df, x=x_col, y=y_col, color=color)
    elif tipo_grafico == 'bar':
        fig = sns.barplot(data=df, x=x_col, y=y_col, color=color)
    elif tipo_grafico == 'hist':
        fig = sns.histplot(df[x_col], color=color)
    
    else:
        raise ValueError(f"Tipo de gráfico '{tipo_grafico}' no soportado.")
    fig.set(xlabel=x_col_name,ylabel=y_col_name)
    x = random.randint(0, 100000) 
    save_results_to = settings.temp_files
    archivo = plt.savefig(save_results_to + str(x) + ".png")
    return archivo, x