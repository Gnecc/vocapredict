#!/bin/sh
set -eu

flyctl deploy --config backend/fly.toml -a macso-patient-dream-1724 backend
flyctl deploy --config frontend/fly.toml -a ionic-react-quiz-app frontend
