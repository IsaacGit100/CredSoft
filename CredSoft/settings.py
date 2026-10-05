"""
Django settings for CredSoft project.
"""
import pymysql
pymysql.install_as_MySQLdb()

from pathlib import Path
import os

from pathlib import Path
import os

from decouple import config


DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "hi-wavescoders.com",
    "www.hi-wavescoders.com",
]

os.environ['DJANGO_LEDGER_USE_DEPRECATED_BEHAVIOR'] = 'True'
import warnings
warnings.filterwarnings("ignore", module="django_ledger.models.deprecations")

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Your custom apps
    "core",
    "SysSetup",
    "UserAuth",
    "MembersApp.apps.MembersAppConfig",
    "coa",
    "LoanApp",
    "RecPayApp",
    "FinanceApp",
    "InvestApp",
    "help_module",
    "CustomReports",
    "crispy_forms",
    "CoreApp",
    "Supervisor",
    "LoginApp",
    "services",
    "BackupRestore",
    "reset",
    "AndyApp",
    "FixedAssets",
    "OpenBals",
    "django_ledger",
    #    'djan_led',
    "djan_led.apps.DjanLedConfig",
    "ChurchApp",
    "Consolidated",
    "website",
    "POS",
    "CreditUnion",
    "Dividend",
    "Tech",
    "DocMgt",
    "Images",
    "Report",
    "AutoServices",
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
   
]

ROOT_URLCONF = 'CredSoft.urls'

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
                "SysSetup.context_processors.system_settings",
                "help_module.context_processors.help_context",
                "djan_led.context_processors.current_entity",
                "djan_led.context_processors.entity_config",
                "Consolidated.context_processors.current_context",
            ],
        },
    },
]

WSGI_APPLICATION = 'CredSoft.wsgi.application'


# SECRET_KEY = 'django-insecure-8#uhl1f@...'


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode=''",
            "charset": "utf8mb4",
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-GH'
TIME_ZONE = 'Africa/Accra'
USE_I18N = True
USE_TZ = True
CURRENCY_SYMBOL = 'GH₵'
LOCALE_NAME = 'en_GH'


# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Also ensure you have this for static files


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/redirect/'


# Session settings
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True

# Message tags for Bootstrap
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
    messages.INFO: 'info',
    messages.WARNING: 'warning',
}

CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Add this to your settings.py temporarily
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

SESSION_COOKIE_AGE = 7200  # 2 hours
SESSION_SAVE_EVERY_REQUEST = True
