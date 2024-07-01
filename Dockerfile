# Usa una imagen base oficial de Python 3.9
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos a /app
COPY requirements.txt .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del directorio actual en /app
COPY . .

# Expone el puerto 8007 para el contenedor
EXPOSE 8007

# Comando para ejecutar la aplicación FastAPI usando uvicorn
# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8007"]
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8007", "--reload"]