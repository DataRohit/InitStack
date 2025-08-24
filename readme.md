# InitStack

<!-- Project Status -->
[![Project Status: Active](https://img.shields.io/badge/Project%20Status-Active-brightgreen)](https://github.com/DataRohit/InitStack)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./license)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](#)
[![Coverage: 100%](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)](#)

<!-- Core Technologies -->
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3130/)
[![Django](https://img.shields.io/badge/Django-5.2.5-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-ff1709.svg?logo=fastapi&logoColor=white)](https://www.django-rest-framework.org/)
[![Celery](https://img.shields.io/badge/Celery-5.5.3-brightgreen.svg?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-7.17.x-005571.svg?logo=elasticsearch&logoColor=white)](https://www.elastic.co/)
[![Redis](https://img.shields.io/badge/Redis-Stack-red.svg?logo=redis&logoColor=white)](https://redis.io/)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-1.36.0-009688.svg?logo=opentelemetry&logoColor=white)](https://opentelemetry.io/)
[![Sentry](https://img.shields.io/badge/Sentry-Error%20Tracking-362D59.svg?logo=sentry&logoColor=white)](https://sentry.io/)

<!-- Infrastructure -->
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Nginx](https://img.shields.io/badge/Nginx-Web%20Server-009639.svg?logo=nginx&logoColor=white)](https://www.nginx.com/)
[![Jaeger](https://img.shields.io/badge/Jaeger-Tracing-0077B6.svg?logo=jaeger&logoColor=white)](https://www.jaegertracing.io/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C.svg?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![MinIO](https://img.shields.io/badge/MinIO-Object%20Storage-2F4A70.svg?logo=minio&logoColor=white)](https://min.io/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-Message%20Broker-FF6600.svg?logo=rabbitmq&logoColor=white)](https://www.rabbitmq.com/)
[![Mailpit](https://img.shields.io/badge/Mailpit-Email%20Testing-009688.svg)](https://github.com/axllent/mailpit)
[![SonarQube](https://img.shields.io/badge/SonarQube-Code%20Quality-A0C4FF.svg?logo=sonarqube&logoColor=white)](https://www.sonarqube.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![PGAdmin](https://img.shields.io/badge/pgAdmin-UI-306998.svg?logo=postgresql&logoColor=white)](https://www.pgadmin.org/)
[![Kibana](https://img.shields.io/badge/Kibana-Data%20Visualization-0077B6.svg?logo=kibana&logoColor=white)](https://www.elastic.co/kibana)

**A Robust Backend Template For Building Scalable And Observable APIs With Django, Celery, Docker, And OpenTelemetry.**

## 🌟 Features

### Core Features

- **⚡ Django + DRF**: Production-Grade Web Framework And REST Toolkit.
- **📦 Docker & Compose**: Reproducible Dev/Prod Environments.
- **📊 OpenTelemetry**: Distributed Tracing And Metrics Exported To Collector.
- **⚙️ Celery + RabbitMQ**: Background Task Processing & Scheduling (Beat).
- **💾 Redis**: Caching And Django Cache Backend.
- **🔍 Elasticsearch + Kibana**: Search, Analytics, And Visualization.
- **📈 Prometheus**: Metrics Scraping With Ready-To-Use Config.
- **📧 Email Services**: Async Email With `djcelery_email` And Mailpit.
- **☁️ Object Storage**: S3-Compatible Storage (MinIO) Via `django-storages`.
- **🚨 Sentry**: Error Tracking With Integrations (Django, Celery, Redis, Boto3).
- **🕸️ Nginx**: Edge Proxy To App And Static/Media.
- **🧭 Health Checks**: `django-health-check` + Custom Checks (Jaeger, Prometheus, Mailpit, Elasticsearch).

### Development Tooling

- **Ruff** Linting, **Mypy** Type Checking, **Pytest** + Coverage.
- **Djlint** For Templates, **Django Extensions**, **Factory Boy** + **Faker**.
- **SonarQube** Integration Via `make sonar-scan`.
- **100% Test Coverage Enforced** (Pytest With `--cov-fail-under=100`).

## 🛠️ Tech Stack

- **Framework**: Django 5.2.5, DRF 3.16.1
- **Task Queue**: Celery 5.5.3, Flower
- **Broker / Cache**: RabbitMQ, Redis Stack
- **Search**: Elasticsearch 7.17.x, Kibana
- **Database**: PostgreSQL (With pgAdmin)
- **Observability**: OpenTelemetry Collector, Jaeger, Prometheus, Sentry
- **Storage**: MinIO (S3-Compatible) via `django-storages`
- **Web**: Nginx Fronting Django

## 🚀 Getting Started

### Prerequisites

- Docker And Docker Compose (Or Podman)
- Git
- Python 3.13 (For Local Tooling/Management If Needed)
- Make (Optional, For Using The Makefile)

### 1) Clone Repository

```bash
git clone https://github.com/DataRohit/InitStack.git
cd InitStack
```

### 2) Configure Environment

Copy `.env.example` To `.env` For Each Service:

```bash
cp .envs/django/.env.example .envs/django/.env
cp .envs/postgres/.env.example .envs/postgres/.env
cp .envs/elasticsearch/.env.example .envs/elasticsearch/.env
cp .envs/kibana/.env.example .envs/kibana/.env
cp .envs/jaeger/.env.example .envs/jaeger/.env
cp .envs/redis/.env.example .envs/redis/.env
cp .envs/rabbitmq/.env.example .envs/rabbitmq/.env
cp .envs/minio/.env.example .envs/minio/.env
cp .envs/pgadmin/.env.example .envs/pgadmin/.env
cp .envs/mailpit/.env.example .envs/mailpit/.env
cp .envs/celery-flower/.env.example .envs/celery-flower/.env
```

Notes:

- Keep Secrets In `.env` Files; Do Not Commit.
- `config/settings.py` reads from `.env` and provides secure production defaults.

### 3) Build And Run

Using Docker Compose:

```bash
make docker-up
```

Or With Podman:

```bash
make podman-up
```

### 4) Access Services

- **Nginx (App Gateway):** <http://localhost:8080>
- **Django Admin:** <http://localhost:8080/admin/>
- **Django Health:** <http://localhost:8080/health/>
- **DRF Schema:** <http://localhost:8080/api/swagger/schema/>
- **Swagger UI:** <http://localhost:8080/api/swagger/ui/>
- **ReDoc:** <http://localhost:8080/api/swagger/redoc/>
- **Flower:** <http://localhost:5555>
- **Redis Insight (Stack UI):** <http://localhost:8001>
- **Kibana:** <http://localhost:5601>
- **Elasticsearch:** <http://localhost:9200>
- **Jaeger UI:** <http://localhost:16686>
- **Prometheus:** <http://localhost:9090>
- **Mailpit:** <http://localhost:8025>
- **MinIO Console:** <http://localhost:9080>
- **pgAdmin:** <http://localhost:5050>
- **SonarQube:** <http://localhost:9000>

Ports And Mappings Are Defined In `docker-compose.yml`.

## ⚙️ Configuration Highlights

- `config/settings.py`
  - PostgreSQL As Default DB (`POSTGRES_*` envs)
  - Redis: Cache Backend (`REDIS_URL`)
  - RabbitMQ: Celery Broker (`RABBITMQ_URL`)
  - Celery Result Backend: Elasticsearch (`ELASTICSEARCH_URL`)
  - Email Backend: `djcelery_email` -> Mailpit (`DJANGO_EMAIL_*`)
  - Storage: `django-storages` S3 Backend Targeting MinIO (`DJANGO_AWS_*`)
  - DRF + Spectacular (Swagger/Redoc), CORS Config
  - Sentry SDK With Integrations
  - OpenTelemetry Service Metadata And OTLP Endpoint

- `config/opentelemetry.py`
  - Initializes Tracer Provider, OTLP HTTP Exporter
  - Auto-Instruments Django, Celery, Requests, Redis, Psycopg, Elasticsearch, Botocore, Pika

- `config/celery_app.py`
  - Celery App With Broker/Backend From Settings, Logging Wiring, Autodiscovery

- Health Checks (`apps/common/health_checks/`)
  - Custom Checks For Elasticsearch, Jaeger, Prometheus, Mailpit

## 🧪 Development

Run Linting / Type Checking / Tests Locally:

```bash
make ruff-check  # or 'make ruff-lint' to auto-fix issues
mypy .
pytest -q
```

- Coverage Threshold Is Enforced At 100% Via `pytest.ini` (`--cov-fail-under=100`).
- HTML Coverage Report Is Generated At `htmlcov/index.html`.

Ruff/Mypy/Pytest Are Configured In `pyproject.toml`.

## 📝 Makefile Commands

- **help** — Show This Help Message

- **Code Analysis:**
  - `ruff-check` — Run Ruff Linter In Check Mode
  - `ruff-lint` — Run Ruff Linter With Auto-Fix
  - `sonar-scan` — Run SonarQube Analysis (Requires `SONAR_TOKEN` Env Var)

- **Docker:**
  - `docker-build` — Build All Services
  - `docker-up` — Build And Start All Services
  - `docker-down` — Stop And Remove Services
  - `docker-restart` — Restart All Services
  - `docker-clean` — Clean Unused Docker Resources

- **Podman:**
  - `podman-build` — Build All Services
  - `podman-up` — Build And Start All Services
  - `podman-down` — Stop And Remove Services
  - `podman-restart` — Restart All Services
  - `podman-clean` — Clean Unused Podman Resources

- **clean-all** — Remove Python And Tooling Artifacts

## 🔐 Environment Variables

Environment Variables Are Loaded From `.envs/*/.env`. Key Groups:

- Django: `DJANGO_*` (Debug, Secret Key, Hosts, Email, CORS, Security)
- Database: `POSTGRES_*`
- Broker/Cache: `RABBITMQ_URL`, `REDIS_URL`
- Search: `ELASTICSEARCH_URL`
- Storage: `DJANGO_AWS_*` (S3/MinIO)
- Observability: `OTEL_*`, `SENTRY_*`, `JAEGER_*`, `PROMETHEUS_*`

Never Commit Secrets. Use Strong, Per-Environment Values.

## 📦 Dependencies

Pinned In `requirements.txt`. Notables: Django, DRF, Celery, Redis, Elasticsearch, Sentry SDK, OpenTelemetry, DRF Spectacular, Django Health Check, Django Storages, Mypy, Ruff, Pytest.

## ❗ Notes & Tips

- Health Endpoints Are Available Under `/health/` (Enabled In Debug).
- Nginx Container Probes `/health/`; Django Provides Health URLs Via `django-health-check` And Custom Checks.
- Static/Media Are Configured To Serve From S3/MinIO Backends.
- SSL/HSTS/Cookies Are Secure By Default; Override In Dev `.env` As Needed.

## 📄 License

This Project Is Licensed Under The MIT License — See The [`license`](./license) File For Details.

## 📞 Contact

Rohit Ingole — <datarohit@outlook.com>

Project Link: <https://github.com/DataRohit/InitStack>
