# VocaPredict Frontend

Frontend web para responder 48 actividades RIASEC y enviar seis puntajes al backend de recomendaciones.

## Requisitos

- Node.js 16 recomendado para este proyecto basado en Create React App 4.
- npm.

## Instalacion

```bash
npm ci
```

## Configuracion local

Crea `frontend/.env.local` cuando quieras apuntar a un backend local:

```bash
REACT_APP_API_URL=http://localhost:8080
```

En desarrollo, si no se define, la app usa `http://localhost:8080`. La compilación Docker requiere `REACT_APP_API_URL`; `fly.toml` indica el backend de Fly. Despliega el backend RIASEC actualizado antes de publicar este frontend.

## Desarrollo

```bash
npm start
```

La app abre en `http://localhost:3000`.

## Build

Con Node 17 o superior:

```bash
NODE_OPTIONS=--openssl-legacy-provider npm run build
```

Con Node 16:

```bash
npm run build
```

## Flujo de la app

- `/home`: instrucciones e inicio del cuestionario.
- `/questions`: 48 actividades RIASEC calificadas de 1 a 5.
- `/results`: seis puntajes normalizados y envío al backend.
- `/prediction`: cuatro familias vocacionales con carreras sugeridas para explorar.
