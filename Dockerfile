# Usamos la imagen oficial de Python 3.12 slim para reducir el tamaño
FROM python:3.12-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero el requirements.txt para aprovechar la caché de Docker
# Si no cambian las dependencias, Docker no las reinstala en cada build
COPY requirements.txt .

# Instalamos las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del proyecto
COPY . .

# Exponemos el puerto 8000 que usa Django
EXPOSE 8000

# Comando para arrancar el servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]