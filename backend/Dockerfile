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

# Copia el servicio y el artefacto RIASEC ya entrenado
COPY serve.py family_prediction.py ./
COPY riasec_model.joblib riasec_families.joblib ./
COPY red_semantica/riasec_owl.py red_semantica/catalogo_riasec.json ./red_semantica/

EXPOSE 8080

# Uvicorn debe escuchar en 0.0.0.0:8080 para Fly
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8080"]
