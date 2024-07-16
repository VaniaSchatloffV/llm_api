#!/bin/bash

# Verificar si el entorno virtual existe y eliminarlo si es así
if [ -d "venv" ]; then
  echo "Eliminando el entorno virtual existente..."
  rm -rf venv
fi

# Crear un nuevo entorno virtual
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate

# Instalar las dependencias
pip install --no-cache-dir -r requirements.txt

# Establecer variables de entorno
export $(grep -v '^#' .env | xargs)

# Ejecutar la aplicación
uvicorn api:app --port 8007 --reload
