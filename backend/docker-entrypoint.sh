#!/bin/sh
set -e

alembic upgrade head

# "true": demo hesapları yoksa oluştur. "reset": her açılışta tarihleri bugüne göre yeniden üret.
case "$SEED_DEMO" in
  true) python -m app.seed ;;
  reset) python -m app.seed --reset ;;
esac

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
