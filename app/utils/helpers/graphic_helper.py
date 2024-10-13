import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from app.dependencies import get_settings

settings = get_settings()
def generar_grafico(csv_path, tipo_grafico, x_col, y_col=None, color=None, titulo=None):
    # Cargar el archivo CSV en un DataFrame de pandas

    if color is None:
        color = 'blue'  # Valor por defecto para el color
    if titulo is None:
        titulo = 'Gráfico generado'  # Valor por defecto para el título

    df = pd.read_csv(csv_path)

    plt.figure()
    if titulo:
        plt.title(titulo)

    # Dependiendo del tipo de gráfico, generar la visualización
    if tipo_grafico == 'scatter':
        sns.scatterplot(data=df, x=x_col, y=y_col, color=color)
    elif tipo_grafico == 'line':
        sns.lineplot(data=df, x=x_col, y=y_col, color=color)
    elif tipo_grafico == 'bar':
        sns.barplot(data=df, x=x_col, y=y_col, color=color)
    elif tipo_grafico == 'hist':
        sns.histplot(df[x_col], color=color)
    else:
        raise ValueError(f"Tipo de gráfico '{tipo_grafico}' no soportado.")
    
    # Mostrar el gráfico
    #plt.show()
    x = random.randint(0, 100000) 
    save_results_to = settings.temp_files
    archivo = plt.savefig(save_results_to + str(x) + ".png")
    print(x)
    return archivo, x

# Ejemplo de uso
# generar_grafico('datos.csv', 'scatter', 'columna_x', 'columna_y')