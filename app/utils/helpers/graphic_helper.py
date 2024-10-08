import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from app.dependencies import get_settings

settings = get_settings()
def generar_grafico(csv_path, tipo_grafico, x_col, y_col=None):
    # Cargar el archivo CSV en un DataFrame de pandas
    df = pd.read_csv(csv_path)

    # Dependiendo del tipo de gráfico, generar la visualización
    if tipo_grafico == 'scatter':
        sns.scatterplot(data=df, x=x_col, y=y_col)
    elif tipo_grafico == 'line':
        sns.lineplot(data=df, x=x_col, y=y_col)
    elif tipo_grafico == 'bar':
        sns.barplot(data=df, x=x_col, y=y_col)
    elif tipo_grafico == 'hist':
        sns.histplot(df[x_col])
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