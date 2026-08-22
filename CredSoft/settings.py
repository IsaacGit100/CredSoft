"""
Django settings for CredSoft project.
"""

from pathlib import Path
import os

from decouple import config

DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = ["hi-wavescoders.com", "www.hi-wavescoders.com"]

os.environ['DJANGO_LEDGER_USE_DEPRECATED_BEHAVIOR'] = 'True'
import warnings
warnings.filterwarnings("ignore", module="django_ledger.models.deprecations")

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8#uhl1f@w56z9r&j*r0w8-o28sra&6_$_71^ns-hfw)l2$x*7k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    
    # Your custom apps
    'core',
    'SysSetup',
    'UserAuth',
    'MembersApp',
    'coa',
    'LoanApp',
    'RecPayApp',
    'FinanceApp',
    'InvestApp',
    'help_module',
   
    'CustomReports',
    'crispy_forms',
    'CoreApp',
    'Supervisor',
    'LoginApp',
    'services',
    'BackupRestore',
    'reset',
    'AndyApp',
    'FixedAssets',
    'OpenBals',
    'django_ledger',
#    'djan_led',
    'djan_led.apps.DjanLedConfig',
    'ChurchApp',
    'Consolidated',
    'website',
    'CredApp',
    'POS',
    'CreditUnion',
    'Dividend',
    'Tech',
    
   
    
    
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
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
    
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'SysSetup.context_processors.system_settings',
                'help_module.context_processors.help_context',
                'djan_led.context_processors.current_entity',
                
           
            ],
        },
    },
]

WSGI_APPLICATION = 'CredSoft.wsgi.application'


# Use SQLite3 for now
#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.sqlite3",
#        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
#    }
#}

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


#DATABASE - Using SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'credsoft_db',   # <-- Same database for both
        'USER': 'postgres',
        'PASSWORD': 'BigOne1',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
#        'NAME': 'CredDb',
#        'USER': 'CredUser',
#        'HOST': 'localhost',
#        'PASSWORD': 'BigOne1',
#        'PORT': '3306',
#    }
# }

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
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Also ensure you have this for static files


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/Logout URLs
# LOGIN_URL = 'userauth:login'
# LOGIN_REDIRECT_URL = 'userauth:dashboard'
# LOGOUT_REDIRECT_URL = 'userauth:login'


# LOGIN_URL = '/login/'           # Where to go if not logged in
# LOGIN_REDIRECT_URL = '/'        # Where to go after successful login
# LOGOUT_REDIRECT_URL = '/login/' # Where to go after logout


LOGIN_URL = '/accounts/login/'
# LOGIN_REDIRECT_URL = '/redirect/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# LOGIN_REDIRECT_URL = '/djan_led/redirect/'
LOGIN_REDIRECT_URL = '/redirect/'


# LOGIN_URL = 'core:login'
# LOGIN_REDIRECT_URL = 'core:dashboard'
# LOGOUT_REDIRECT_URL = 'core:login'

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
