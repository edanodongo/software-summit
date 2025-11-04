from pathlib import Path
import json
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Try loading config.json if it exists, otherwise use safe defaults (for CI)
config_path = BASE_DIR / "config.json"

if config_path.exists():
    with open(config_path) as config_file:
        config = json.load(config_file)
else:
    # Default configuration for GitHub Actions or local tests
    config = {
        "SECRET_KEY": os.getenv("SECRET_KEY", "dummy-key-for-tests"),
        "DATABASE": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3"
        }
    }


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.get('DEBUG', True)

ALLOWED_HOSTS = config['ALLOWED_HOSTS']

# API KEY FOR REG SERVICE
REG_SERVICE_API_KEY = config['REG_SERVICE_API_KEY']

# === Rate Limit Settings ===
RATE_LIMIT_REQUESTS = 60      # Max number of requests allowed
RATE_LIMIT_PERIOD = 60        # In seconds (1 minute)



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'summitPage',
    'rest_framework',
    'django_countries',
]


LOGIN_URL = "custom_login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "custom_login"


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'summit.middleware.AutoLogoutMiddleware',
]

ROOT_URLCONF = 'summit.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'summit.wsgi.application'




DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config['DB_DEFAULT_NAME'],
        'USER': config['DB_DEFAULT_USER'],
        'PASSWORD': config['DB_DEFAULT_PASSWORD'],
        'HOST': config['DB_DEFAULT_HOST'],
        'PORT': config['DB_DEFAULT_PORT'],
    },
}



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

# Tell Django to look for static files both inside the app and in the global static folder
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Only used in production (when running `collectstatic`)
STATIC_ROOT = BASE_DIR / "static_root"
MEDIA_ROOT = BASE_DIR / "media_root"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = config['EMAIL_BACKEND']
EMAIL_HOST = config['EMAIL_HOST']
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = config['EMAIL_HOST_PASSWORD']
DEFAULT_FROM_EMAIL = config['DEFAULT_FROM_EMAIL']


# Auto logout after minutes of inactivity
AUTO_LOGOUT_TIMEOUT = 60 * 15

SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 days max
SESSION_SAVE_EVERY_REQUEST = True        # resets expiry on each request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # for Remember Me on login page

#  python -c "import uuid; print(uuid.uuid4())"
SPECIAL_ACCESS_KEY = "ce9e2f46-2579-4467-a856-05a04d0caac5"
