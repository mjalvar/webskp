FROM python:3.11-slim

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

WORKDIR /app

# Copiar requerimientos e instalar dependencias del backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y carpetas estáticas al contenedor
COPY . .

# Asegurar que existan las carpetas de modelos estáticos
RUN mkdir -p static/models

# Exponer el puerto predeterminado que usa Uvicorn
EXPOSE 8080

# Comando para arrancar el servidor en producción
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
