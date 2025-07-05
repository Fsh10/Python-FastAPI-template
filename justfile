default:
  just -l

run-dev:
  ENV_FILE=.env.dev poetry run uvicorn src.main:app --reload

run-stage:
  ENV_FILE=.env.stage poetry run uvicorn src.main:app --reload

run-prod:
  ENV_FILE=.env.prod poetry run uvicorn src.main:app --reload

create-revision MESSAGE:
  alembic revision --autogenerate -m "{{MESSAGE}}"

upgrade-dev:
  ENV_FILE=.env.dev poetry run alembic upgrade head

upgrade-stage:
  ENV_FILE=.env.stage poetry run alembic upgrade head

upgrade-prod:
  ENV_FILE=.env.prod poetry run alembic upgrade head

downgrade LEVEL:
  alembic downgrade {{LEVEL}}

test:
  ENV_FILE=.env.dev ENVIRONMENT=TESTING pytest -v

ruff:
  ruff format .
  ruff check --fix --unsafe-fixes

up:
  docker-compose up -d

build:
  docker-compose build

ps:
  docker-compose ps

build-push-prod:
  docker build -t your-registry.com/your-project:prod -f Dockerfile.prod .
  docker push your-registry.com/your-project:prod
  

build-push-stage:
  docker build -t your-registry.com/your-project:stage -f Dockerfile.prod .
  docker push your-registry.com/your-project:stage

build-push-dev:
  docker build -t your-registry.com/your-project:dev .
  docker push your-registry.com/your-project:dev

celery-worker-dev:
  ENV_FILE=.env.dev poetry run celery -A src.celery:celery worker --loglevel=info

celery-worker-stage:
  ENV_FILE=.env.stage poetry run celery -A src.celery:celery worker --loglevel=info

celery-worker-prod:
  ENV_FILE=.env.prod poetry run celery -A src.celery:celery worker --loglevel=info

celery-beat-dev:
  ENV_FILE=.env.dev poetry run celery -A src.celery:celery beat --loglevel=info

celery-beat-stage:
  ENV_FILE=.env.stage poetry run celery -A src.celery:celery beat --loglevel=info

celery-beat-prod:
  ENV_FILE=.env.prod poetry run celery -A src.celery:celery beat --loglevel=info
