# VocaPredict Monorepo

Este repositorio contiene el backend de prediccion vocacional y el frontend Ionic React en una sola base de codigo.

## Estructura

```text
.
|-- backend/   # FastAPI, modelo SVM, entrenamiento y artefactos
|-- frontend/  # Ionic React / Capacitor
`-- scripts/   # Automatizaciones del monorepo
```

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn serve:app --host 0.0.0.0 --port 8080
```

La API principal expone:

```http
POST /predict
```

La documentacion detallada del backend esta en `backend/README.md`.

## Frontend

```bash
cd frontend
npm ci
npm start
```

Para apuntar el frontend a otra API, crea `frontend/.env.local`:

```bash
REACT_APP_API_URL=http://localhost:8080
```

En Fly, el valor por defecto apunta al backend desplegado en `https://macso-patient-dream-1724.fly.dev`.

Si usas Node 17 o superior para compilar localmente este frontend basado en CRA 4, ejecuta:

```bash
NODE_OPTIONS=--openssl-legacy-provider npm run build
```

El Dockerfile del frontend usa Node 16 para evitar ese problema durante el despliegue.

## CORS

El backend permite por defecto estos origenes:

- `http://localhost:3000`
- `http://localhost:8100`
- `https://ionic-react-quiz-app.fly.dev`

Puedes sobreescribirlos en Fly con:

```bash
flyctl secrets set CORS_ORIGINS=https://tu-frontend.fly.dev --config backend/fly.toml
```

## Despliegue en Fly.io

El monorepo mantiene dos apps Fly, una para cada runtime:

- `backend/fly.toml`: FastAPI + Uvicorn.
- `frontend/fly.toml`: build React + Nginx.

Desde la raiz puedes desplegar cada app:

```bash
flyctl deploy backend --config backend/fly.toml
flyctl deploy frontend --config frontend/fly.toml
```

O desplegar ambas con un solo comando local:

```bash
sh scripts/deploy-all.sh
```

El workflow de GitHub Actions despliega backend y luego frontend en cada push a `main`.
