import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    plt.show()

# Ejemplo de uso
# generar_grafico('datos.csv', 'scatter', 'columna_x', 'columna_y')