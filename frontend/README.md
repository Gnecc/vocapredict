# VocaPredict Frontend

Frontend web para responder el cuestionario vocacional corto y enviar los puntajes al backend de prediccion.

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

Si no se define, la app usa el backend desplegado configurado en el codigo.

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
- `/questions`: cuestionario de intereses de 27 reactivos.
- `/results`: resumen de puntajes y envio al backend.
- `/prediction`: prediccion y probabilidades devueltas por el modelo.
