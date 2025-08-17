# Standard Library Imports
import logging
import ssl
from pathlib import Path

# Third Party Imports
import environ
import sentry_sdk
from sentry_sdk.integrations.boto3 import Boto3Integration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# Set The Project Base Directory
BASE_DIR: Path = Path(__file__).resolve(strict=True).parent.parent

# Set The Apps Directory
APPS_DIR: Path = BASE_DIR / "apps"

# Set The Environ Object
env = environ.Env()

# Set Project Name
PROJECT_NAME: str = "InitStack"

# Set The Debug Mode
DEBUG: bool = env.bool(
    var="DJANGO_DEBUG",
    default=False,
)

# Set The Secret Key
SECRET_KEY: str = env.str(
    var="DJANGO_SECRET_KEY",
    default="ofem&p9js4_b%yde%)t@pwy!0=z2&3uylejc3xoowbn7-jtx9z#bt=#k+u)7hk*3@s4f_n)64^d7u)#0&xj09s)0op%)x1&9jcle",
)

# Set The Allowed Hosts
ALLOWED_HOSTS: list[str] = env.list(
    var="DJANGO_ALLOWED_HOSTS",
    default=["api.initstack.serveo.net"],
)

# Set The Time Zone
TIME_ZONE: str = env.str(
    var="DJANGO_TIME_ZONE",
    default="Asia/Kolkata",
)

# Set The Language Code
LANGUAGE_CODE: str = "en-us"

# Set The Site ID
SITE_ID: int = 1

# Set The Use I18N
USE_I18N: bool = True

# Set The Use TZ
USE_TZ: bool = True

# Set The Databases
DATABASES: dict[str, dict[str, str]] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str(
            var="POSTGRES_DB",
            default="initstack",
        ),
        "USER": env.str(
            var="POSTGRES_USER",
            default="xgg3HtoYRw2LUT4",
        ),
        "PASSWORD": env.str(
            var="POSTGRES_PASSWORD",
            default="jqxipLMtuCO3gPq",
        ),
        "HOST": env.str(
            var="POSTGRES_HOST",
            default="postgres-service",
        ),
        "PORT": env.str(
            var="POSTGRES_PORT",
            default="5432",
        ),
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 60,
    },
}

# Set The Default Auto Field
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# Set The Root URL Configuration
ROOT_URLCONF: str = "config.urls"

# Set The WSGI Application
WSGI_APPLICATION: str = "config.wsgi.application"

# Set The ASGI Application
ASGI_APPLICATION: str = "config.asgi.application"

# Set The Django Apps
DJANGO_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.forms",
]

# Set The Third Party Apps
THIRD_PARTY_APPS: list[str] = [
    "collectfasta",
    "corsheaders",
    "djcelery_email",
    "django_celery_beat",
    "django_extensions",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
    "health_check.contrib.celery",
    "health_check.contrib.celery_ping",
    "health_check.contrib.psutil",
    "health_check.contrib.s3boto3_storage",
    "health_check.contrib.rabbitmq",
    "health_check.contrib.db_heartbeat",
    "rest_framework",
    "silk",
]

# Set The Local Apps
LOCAL_APPS: list[str] = [
    "apps.common",
    "apps.users",
]

# Set The Apps
INSTALLED_APPS: list[str] = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Set The Redis Default URL
REDIS_DEFAULT_URL: str = env.str(
    var="REDIS_DEFAULT_URL",
    default="redis://:WFyzhcO3ByZIjdd@redis-service:6379/0",
)

# Set The Redis Token Cache URL
REDIS_TOKEN_CACHE_URL: str = env.str(
    var="REDIS_TOKEN_CACHE_URL",
    default="redis://:WFyzhcO3ByZIjdd@redis-service:6379/1",
)

# Set The RabbitMQ URL
RABBITMQ_URL: str = env.str(
    var="RABBITMQ_URL",
    default="amqp://NGeDFwAgoZwmMvP:ftT4tT0Qy2cQXGm@rabbitmq-service:5672/",
)

# Set The Elasticsearch URL
ELASTICSEARCH_URL: str = env.str(
    var="ELASTICSEARCH_URL",
    default="elasticsearch://elastic:KBReYFzIVHVGiHk@elasticsearch-service:9200/celery_results",
)

# Set The Health Check
HEALTH_CHECK: dict[str, int] = {
    "DISK_USAGE_MAX": 90,
    "MEMORY_MIN": 128,
}

# Set The Broker URL
BROKER_URL: str = RABBITMQ_URL


# Set The Migration Modules
MIGRATION_MODULES: dict[str, str] = {"sites": "apps.contrib.sites.migrations"}

# Set The Authentication Backends
AUTHENTICATION_BACKENDS: list[str] = ["django.contrib.auth.backends.ModelBackend"]

# Set The Password Hashers
PASSWORD_HASHERS: list[str] = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Set The Password Validators
AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Set The User Model
AUTH_USER_MODEL: str = "users.User"

# Set The Middleware
MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "silk.middleware.SilkyMiddleware",
]

# Set The Static Root
STATIC_ROOT: str = str(BASE_DIR / "staticfiles")

# Set The Static URL
STATIC_URL: str = "/static/"

# Set The Static Files Directories
STATICFILES_DIRS: list[str] = []

# Set The Static Files Finders
STATICFILES_FINDERS: list[str] = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Set The Media Root
MEDIA_ROOT: str = str(APPS_DIR / "media")

# Set The Media URL
MEDIA_URL: str = "/media/"

# Set The Templates
TEMPLATES: list[dict[str, str]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Set The Form Renderer
FORM_RENDERER: str = "django.forms.renderers.TemplatesSetting"

# Set The Fixtures Directories
FIXTURE_DIRS: tuple[str] = (str(APPS_DIR / "fixtures"),)

# Set The Session Cookie HttpOnly
SESSION_COOKIE_HTTPONLY: bool = True

# Set The Secure Proxy SSL Header
SECURE_PROXY_SSL_HEADER: tuple[str, str] = ("HTTP_X_FORWARDED_PROTO", "https")

# Set The Secure SSL Redirect
SECURE_SSL_REDIRECT: bool = env.bool(
    var="DJANGO_SECURE_SSL_REDIRECT",
    default=True,
)

# Set The Session Cookie Secure
SESSION_COOKIE_SECURE: bool = env.bool(
    var="DJANGO_SESSION_COOKIE_SECURE",
    default=True,
)

# If Not Debug
if not DEBUG:
    # Set The Session Cookie Name
    SESSION_COOKIE_NAME: str = "__Secure-sessionid"

# Set The CSRF Cookie HttpOnly
CSRF_COOKIE_HTTPONLY: bool = True

# Set The CSRF Cookie Secure
CSRF_COOKIE_SECURE: bool = env.bool(
    var="DJANGO_CSRF_COOKIE_SECURE",
    default=True,
)

# If Not Debug
if not DEBUG:
    # Set The CSRF Cookie Name
    CSRF_COOKIE_NAME: str = "__Secure-csrftoken"

# Set The CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS: list[str] = env.list(
    var="DJANGO_CSRF_TRUSTED_ORIGINS",
    default=[
        "https://api.initstack.serveo.net",
    ],
)

# Set The X Frame Options
X_FRAME_OPTIONS: str = "DENY"

# Set The Secure HSTS Seconds
SECURE_HSTS_SECONDS: int = 60

# Set The Secure HSTS Include Subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = env.bool(
    var="DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=True,
)

# Set The Secure HSTS Preload
SECURE_HSTS_PRELOAD: bool = env.bool(
    var="DJANGO_SECURE_HSTS_PRELOAD",
    default=True,
)

# Set The Secure Content Type Nosniff
SECURE_CONTENT_TYPE_NOSNIFF: bool = env.bool(
    var="DJANGO_SECURE_CONTENT_TYPE_NOSNIFF",
    default=True,
)

# Set The Email Backend
EMAIL_BACKEND: str = env.str(
    var="DJANGO_EMAIL_BACKEND",
    default="djcelery_email.backends.CeleryEmailBackend",
)

# Set The Email Timeout
EMAIL_TIMEOUT: int = 5

# Set The Email Host
EMAIL_HOST: str = env.str(
    var="DJANGO_EMAIL_HOST",
    default="mailpit-service",
)

# Set The Email Port
EMAIL_PORT: int = env.int(
    var="DJANGO_EMAIL_PORT",
    default=1025,
)

# Set The Default From Email
DEFAULT_FROM_EMAIL: str = env.str(
    var="DJANGO_DEFAULT_FROM_EMAIL",
    default="InitStack <datarohit@outlook.com>",
)

# Set The Server Email
SERVER_EMAIL: str = env.str(
    var="DJANGO_SERVER_EMAIL",
    default=DEFAULT_FROM_EMAIL,
)

# Set The Email Subject Prefix
EMAIL_SUBJECT_PREFIX: str = env.str(
    var="DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[InitStack] ",
)

# Set The Admin URL
ADMIN_URL: str = env.str(
    var="DJANGO_ADMIN_URL",
    default="admin/",
)

# Set The ADMINS
ADMINS: list[tuple[str, str]] = [("Rohit Vilas Ingole", "datarohit@outlook.com")]

# Set The Managers
MANAGERS: list[tuple[str, str]] = ADMINS

# If Debug
if DEBUG:
    # Set The Development Logging
    LOGGING: dict[str, dict[str, str]] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }
else:
    # Set The Production Logging
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "verbose": {
                "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {"level": "INFO", "handlers": ["console"]},
        "loggers": {
            "django.db.backends": {
                "level": "ERROR",
                "handlers": ["console"],
                "propagate": False,
            },
            "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
            "django.security.DisallowedHost": {
                "level": "ERROR",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

# Set The Caches
CACHES: dict[str, dict[str, str]] = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_DEFAULT_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    },
    "token_cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_TOKEN_CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    },
}

# Set The Celery Timezone
CELERY_TIMEZONE: str = TIME_ZONE

# Set The Celery Broker URL
CELERY_BROKER_URL: str = RABBITMQ_URL

# Set The Celery Broker Use SSL
CELERY_BROKER_USE_SSL: bool = {"ssl_cert_reqs": ssl.CERT_NONE} if RABBITMQ_URL.startswith("amqps://") else None

# Set The Celery Result Backend
CELERY_RESULT_BACKEND: str = ELASTICSEARCH_URL

# Set The Celery Redis Backend Use SSL
CELERY_REDIS_BACKEND_USE_SSL: bool = CELERY_BROKER_USE_SSL

# Set The Celery Result Extended
CELERY_RESULT_EXTENDED: bool = True

# Set The Celery Result Backend Always Retry
CELERY_RESULT_BACKEND_ALWAYS_RETRY: bool = True

# Set The Celery Result Backend Max Retries
CELERY_RESULT_BACKEND_MAX_RETRIES: int = 3

# Set The Celery Accept Content
CELERY_ACCEPT_CONTENT: list[str] = ["json"]

# Set The Celery Task Serializer
CELERY_TASK_SERIALIZER: str = "json"

# Set The Celery Result Serializer
CELERY_RESULT_SERIALIZER: str = "json"

# Set The Celery Task Time Limit
CELERY_TASK_TIME_LIMIT: int = 5 * 60

# Set The Celery Task Soft Time Limit
CELERY_TASK_SOFT_TIME_LIMIT: int = 60

# Set The Celery Beat Scheduler
CELERY_BEAT_SCHEDULER: str = "django_celery_beat.schedulers:DatabaseScheduler"

# Set The Celery Worker Send Task Events
CELERY_WORKER_SEND_TASK_EVENTS: bool = True

# Set The Celery Task Send Sent Event
CELERY_TASK_SEND_SENT_EVENT: bool = True

# Set The Celery Worker Hijack Root Logger
CELERY_WORKER_HIJACK_ROOT_LOGGER: bool = False

# Set The Celery Task Eager Propagates
CELERY_TASK_EAGER_PROPAGATES = True

# Set The REST Framework
REST_FRAMEWORK: dict[str, str] = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Set The CORS URLs Regex
CORS_URLS_REGEX: str = r"^/api/.*$"

# Set The CORS Allow Credentials
CORS_ALLOW_CREDENTIALS: bool = True

# Set The CORS Allowed Origins
CORS_ALLOWED_ORIGINS: list[str] = env.list(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    default=[
        "https://api.initstack.serveo.net",
    ],
)

# Set The CORS Allow Methods
CORS_ALLOW_METHODS: list[str] = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# Set The CORS Allow Headers
CORS_ALLOW_HEADERS: list[str] = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Set The Spectacular Settings
SPECTACULAR_SETTINGS: dict[str, str] = {
    "TITLE": "InitStack API",
    "DESCRIPTION": "A High-Performance, Containerized Django Application With Real-Time Processing, Search, Monitoring, And Distributed Task Orchestration Powered By A Modern Cloud-Native Stack.",  # noqa: E501
    "VERSION": "1.0.0",
    "CONTACT": {
        "name": "Rohit Vilas Ingole",
        "url": "https://github.com/datarohit/initstack",
        "email": "datarohit@outlook.com",
    },
    "LICENSE": {
        "name": "MIT License",
        "url": "https://github.com/datarohit/initstack/blob/main/license",
    },
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SCHEMA_PATH_PREFIX": "/api/",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Set The AWS Access Key ID
AWS_ACCESS_KEY_ID: str = env.str(
    var="DJANGO_AWS_ACCESS_KEY_ID",
    default="MD9xH0gT3bD7usp1qZpr",
)

# Set The AWS Secret Access Key
AWS_SECRET_ACCESS_KEY: str = env.str(
    var="DJANGO_AWS_SECRET_ACCESS_KEY",
    default="DQ0uEKEfpo6zdwC0zaiXjpznkaCM1rk6xZOEL2bW",
)

# Set The AWS Storage Bucket Name
AWS_STORAGE_BUCKET_NAME: str = env.str(
    var="DJANGO_AWS_STORAGE_BUCKET_NAME",
    default="initstack",
)

# Set The AWS Query String Auth
AWS_QUERYSTRING_AUTH: bool = False

# Set The AWS Expiry
_AWS_EXPIRY: int = 60 * 60 * 24 * 7

# Set The AWS S3 Object Parameters
AWS_S3_OBJECT_PARAMETERS: dict[str, str] = {
    "CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate",
}

# Set The AWS S3 Max Memory Size
AWS_S3_MAX_MEMORY_SIZE: int = env.int(
    var="DJANGO_AWS_S3_MAX_MEMORY_SIZE",
    default=104_857_600,  # 100MB
)

# Set The AWS S3 Region Name
AWS_S3_REGION_NAME: str = env.str(
    var="DJANGO_AWS_S3_REGION_NAME",
    default="ap-south-1",
)

# Set The AWS S3 Endpoint URL for MinIO
AWS_S3_ENDPOINT_URL: str = env.str(
    var="DJANGO_AWS_S3_ENDPOINT_URL",
    default="http://minio-service:9000",
)

# Set The AWS S3 Custom Domain
AWS_S3_CUSTOM_DOMAIN: str = env.str(
    var="DJANGO_AWS_S3_CUSTOM_DOMAIN",
    default=f"api.initstack.serveo.net/minio/{AWS_STORAGE_BUCKET_NAME}",
)

# Set The AWS S3 Use SSL
AWS_S3_USE_SSL: bool = env.bool(
    var="DJANGO_AWS_S3_USE_SSL",
    default=True,
)

# Set The AWS S3 URL Protocol
AWS_S3_URL_PROTOCOL: str = env.str(
    var="DJANGO_AWS_S3_URL_PROTOCOL",
    default="https:",
)

# Set The AWS S3 Domain
AWS_S3_DOMAIN: str = AWS_S3_CUSTOM_DOMAIN or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

# Set The Media URL
MEDIA_URL: str = f"{AWS_S3_URL_PROTOCOL}//{AWS_S3_DOMAIN}/media/"

# Set The Static URL
STATIC_URL: str = f"{AWS_S3_URL_PROTOCOL}//{AWS_S3_DOMAIN}/static/"

# Set The CollectFASTA Strategy
COLLECTFASTA_STRATEGY: str = "collectfasta.strategies.boto3.Boto3Strategy"

# Set The Storages
STORAGES: dict[str, dict[str, str]] = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "static",
            "default_acl": "public-read",
            "file_overwrite": True,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
        },
    },
    "media": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "media",
            "default_acl": "public-read",
            "file_overwrite": True,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
        },
    },
}

# Set The Sentry DSN
SENTRY_DSN: str = env.str(
    var="DJANGO_SENTRY_DSN",
    default="https://9f12b3c48e5d4a12b7c9d8f6a1b2c3d4@o4839201827364550.ingest.us.sentry.io/4938274650192837",
)

# Set The Sentry Log Level
SENTRY_LOG_LEVEL: int = env.int(
    var="DJANGO_SENTRY_LOG_LEVEL",
    default=logging.INFO,
)

# Set The Sentry Logging
sentry_logging: LoggingIntegration = LoggingIntegration(
    level=SENTRY_LOG_LEVEL,
    event_level=logging.ERROR,
)

# Set The Sentry Integrations
integrations: list[object] = [
    sentry_logging,
    DjangoIntegration(),
    CeleryIntegration(),
    RedisIntegration(),
    Boto3Integration(),
]

# Set The Sentry SDK
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=integrations,
    environment=env.str(
        var="SENTRY_ENVIRONMENT",
        default="production",
    ),
    traces_sample_rate=env.float(
        var="SENTRY_TRACES_SAMPLE_RATE",
        default=0.0,
    ),
)

# Set The OpenTelemetry Exporter OTLP Endpoint
OTEL_EXPORTER_OTLP_ENDPOINT: str = env.str(
    var="OTEL_EXPORTER_OTLP_ENDPOINT",
    default="http://otel-collector-service:4318/v1/traces",
)

# Set The OpenTelemetry Service Name
OTEL_SERVICE_NAME: str = env.str(
    var="OTEL_SERVICE_NAME",
    default="django-service",
)

# Set The OpenTelemetry Service Namespace
OTEL_SERVICE_NAMESPACE: str = env.str(
    var="OTEL_SERVICE_NAMESPACE",
    default="initstack",
)

# Set The OpenTelemetry Service Environment
OTEL_SERVICE_ENVIRONMENT: str = env.str(
    var="OTEL_SERVICE_ENVIRONMENT",
    default="development",
)

# Set The OpenTelemetry Service Version
OTEL_SERVICE_VERSION: str = env.str(
    var="OTEL_SERVICE_VERSION",
    default="0.1.0",
)

# Set The OpenTelemetry Service Instance ID
OTEL_SERVICE_INSTANCE_ID: str = env.str(
    var="OTEL_SERVICE_INSTANCE_ID",
    default="bc956360-9e1e-40e5-b35e-361fb9b87ecc",
)

# Set The Jaeger Query URL
JAEGER_QUERY_URL: str = env.str(
    var="JAEGER_QUERY_URL",
    default="http://jaeger-query-service:16686",
)

# Set The Prometheus URL
PROMETHEUS_URL: str = env.str(
    var="PROMETHEUS_URL",
    default="http://prometheus-service:9090",
)

# Set The JWT Activation Token Secret
ACTIVATION_TOKEN_SECRET: str = env.str(
    var="ACTIVATION_TOKEN_SECRET",
    default="63cd9a95c22f038a141df8434422a7065e0b376957e1ec331725f68246d19994",
)

# Set The JWT Activation Token Expiry
ACTIVATION_TOKEN_EXPIRY: int = env.int(
    var="ACTIVATION_TOKEN_EXPIRY",
    default=1800,
)

# Set The JWT Access Token Secret
ACCESS_TOKEN_SECRET: str = env.str(
    var="ACCESS_TOKEN_SECRET",
    default="5a31c25584d38c02c0f44b29f28575d9199aaecac6072d3fd1115814441ea85b",
)

# Set The JWT Access Token Expiry
ACCESS_TOKEN_EXPIRY: int = env.int(
    var="ACCESS_TOKEN_EXPIRY",
    default=3600,
)

# Set The JWT Refresh Token Secret
REFRESH_TOKEN_SECRET: str = env.str(
    var="REFRESH_TOKEN_SECRET",
    default="8cbf50ee740abf10f9d0f5f0f6d597b48723abec723203fc1e6c63b91c8b2263",
)

# Set The JWT Refresh Token Expiry
REFRESH_TOKEN_EXPIRY: int = env.int(
    var="REFRESH_TOKEN_EXPIRY",
    default=21600,
)

# Set The JWT Change Username Token Secret
CHANGE_USERNAME_TOKEN_SECRET: str = env.str(
    var="CHANGE_USERNAME_TOKEN_SECRET",
    default="f2552c358027c8dba9706eb69f45f8b259c7e5a49a426dc7e859fb6a4e51593a",
)

# Set The JWT Change Username Token Expiry
CHANGE_USERNAME_TOKEN_EXPIRY: int = env.int(
    var="CHANGE_USERNAME_TOKEN_EXPIRY",
    default=1800,
)
