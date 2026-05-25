#!/bin/sh
set -eu

flyctl deploy backend --config backend/fly.toml
flyctl deploy frontend --config frontend/fly.toml
