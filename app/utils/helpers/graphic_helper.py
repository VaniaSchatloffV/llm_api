import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from app.dependencies import get_settings

settings = get_settings()
def generar_grafico(csv_path, tipo_grafico, x_col, y_col=None, color=None, titulo=None, x_col_name=None, y_col_name=None):
    # Cargar el archivo CSV en un DataFrame de pandas

    if color is None:
        color = 'blue'  # Valor por defecto para el color
    if titulo is None:
        titulo = 'Gráfico generado'  # Valor por defecto para el título
    if x_col_name is None: 
        x_col_name = "Eje x"    
    if y_col_name is None: 
        y_col_name = "Eje y" 

    df = pd.read_csv(csv_path)

    plt.figure()
    if titulo:
        plt.title(titulo)

    # Dependiendo del tipo de gráfico, generar la visualización
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
    # Mostrar el gráfico
    #plt.show()
    x = random.randint(0, 100000) 
    save_results_to = settings.temp_files
    archivo = plt.savefig(save_results_to + str(x) + ".png")
    print(x)
    return archivo, x

# Ejemplo de uso
# generar_grafico('datos.csv', 'scatter', 'columna_x', 'columna_y')