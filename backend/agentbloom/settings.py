"""
AgentBloom Django Settings
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-dev-key-change-in-production")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Application definition
INSTALLED_APPS = [
    "daphne",  # ASGI server for Channels
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "django_filters",
    "channels",
    "django_celery_beat",
    "storages",
    "drf_spectacular",
    # AgentBloom apps
    "apps.users",
    "apps.sites",
    "apps.agent",
    "apps.email_crm",
    "apps.courses",
    "apps.calendar_booking",
    "apps.payments",
    "apps.kb",
    "apps.seo",
    "apps.admin_panel",
    "apps.notifications",
    "apps.webhooks",
    "apps.receptionist",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "apps.users.middleware.OrganizationMiddleware",
]

ROOT_URLCONF = "agentbloom.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "agentbloom.wsgi.application"
ASGI_APPLICATION = "agentbloom.asgi.application"

# Database
DATABASES = {
    "default": dj_database_url.config(
        default="postgres://agentbloom:password@localhost:5432/agentbloom",
        conn_max_age=600,
    )
}

# Channel Layers (WebSocket)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("REDIS_URL", "redis://localhost:6379/0")],
        },
    },
}

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    }
}

# Auth
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

# Allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# i18n
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage"
            if not DEBUG else "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "apps.users.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# CORS
CORS_ALLOWED_ORIGINS = os.getenv(
    "DJANGO_CORS_ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# CSRF
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS", "http://localhost:3000"
).split(",")

# Reverse proxy support (Nginx in front of Daphne)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    # Agent: cleanup old conversations weekly
    "agent-cleanup-conversations": {
        "task": "apps.agent.tasks.cleanup_old_conversations",
        "schedule": 604800,  # weekly
    },
    # Agent: run scheduled tasks every 5 minutes
    "agent-run-scheduled-tasks": {
        "task": "apps.agent.tasks.run_scheduled_tasks",
        "schedule": 300,
    },
    # Notifications: cleanup old read notifications daily
    "notifications-cleanup": {
        "task": "apps.notifications.tasks.cleanup_old_notifications",
        "schedule": 86400,  # daily
    },
    # Calendar: send booking reminders every 15 minutes
    "calendar-send-reminders": {
        "task": "apps.calendar_booking.tasks.send_booking_reminders",
        "schedule": 900,
    },
    # KB: run scheduled URL scrapes hourly
    "kb-scrape-urls": {
        "task": "apps.kb.tasks.scrape_scheduled_urls",
        "schedule": 3600,
    },
    # SEO: track keyword rankings daily
    "seo-track-keywords": {
        "task": "apps.seo.tasks.track_keyword_rankings",
        "schedule": 86400,
    },
    # Admin: aggregate platform metrics daily
    "admin-platform-metrics": {
        "task": "apps.admin_panel.tasks.aggregate_platform_metrics",
        "schedule": 86400,
    },
    # Admin: aggregate revenue analytics daily
    "admin-revenue-analytics": {
        "task": "apps.admin_panel.tasks.aggregate_revenue_analytics",
        "schedule": 86400,
    },
    # Admin: system health check every 5 minutes
    "admin-health-check": {
        "task": "apps.admin_panel.tasks.run_system_health_check",
        "schedule": 300,
    },
    # Admin: expire impersonation sessions every minute
    "admin-expire-impersonation": {
        "task": "apps.admin_panel.tasks.expire_impersonation_sessions",
        "schedule": 60,
    },
    # Admin: check moderation queue every hour
    "admin-moderation-queue": {
        "task": "apps.admin_panel.tasks.check_content_moderation_queue",
        "schedule": 3600,
    },
    # Receptionist: aggregate daily analytics
    "receptionist-daily-analytics": {
        "task": "apps.receptionist.tasks.aggregate_daily_analytics",
        "schedule": 86400,
    },
    # Receptionist: close stale sessions every 10 minutes
    "receptionist-close-stale": {
        "task": "apps.receptionist.tasks.close_stale_sessions",
        "schedule": 600,
    },
}

# AWS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET_ASSETS = os.getenv("AWS_S3_BUCKET_ASSETS", "agentbloom-assets")
AWS_S3_BUCKET_SITES = os.getenv("AWS_S3_BUCKET_SITES", "agentbloom-sites")
AWS_CLOUDFRONT_DOMAIN = os.getenv("AWS_CLOUDFRONT_DOMAIN", "")
AWS_STORAGE_BUCKET_NAME = AWS_S3_BUCKET_ASSETS  # default storage bucket
AWS_S3_REGION_NAME = AWS_REGION
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = AWS_CLOUDFRONT_DOMAIN or None

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Email (SES)
EMAIL_BACKEND = "django_ses.SESBackend" if not DEBUG else "django.core.mail.backends.console.EmailBackend"
AWS_SES_REGION_NAME = os.getenv("AWS_SES_REGION", "us-east-1")
AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@nobleblocks.com")

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_LLM_PROVIDER = "openai"
DEFAULT_LLM_MODEL = "gpt-4o"
FALLBACK_LLM_PROVIDER = "claude"
FALLBACK_LLM_MODEL = "claude-4.6"
DESIGN_LLM_PROVIDER = "claude"  # Claude + Gemini both capable; Claude default
DESIGN_LLM_MODEL = "claude-4.6"

# Stock Image APIs
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": "structlog.dev.ConsoleRenderer" if DEBUG else "structlog.processors.JSONRenderer",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# ─── Sentry Error Tracking ─────────────────────────────────────
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN and not DEBUG:
    import sentry_sdk
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        send_default_pii=False,
        environment="production",
    )

# ─── DRF Spectacular (OpenAPI) ─────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "AgentBloom API",
    "DESCRIPTION": "AgentBloom platform API — AI-powered business builder.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}
