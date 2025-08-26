# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Paquetes del sistema mínimos (pandas/openpyxl suelen ir bien así)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependencias primero (mejor cacheo)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código y los artefactos del modelo
COPY serve.py .
COPY svm_model.joblib label_encoder.joblib ./
# (Si tu serve.py lee el .xlsx por alguna razón en runtime, cópialo también)
# COPY conjunto_de_datos_normalizados.xlsx ./

EXPOSE 8080

# Uvicorn debe escuchar en 0.0.0.0:8080 para Fly
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8080"]
