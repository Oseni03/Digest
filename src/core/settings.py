import os
from pathlib import Path
from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+2@26@#tq0z!5e0vgd_bysr0e+p1jre0=&c8=(6f1!#av5mh8b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

HTTP_PROTOCOL = "http"

# Application definition

# TENANTS CONFIGURATION
SHARED_APPS = (
    'django_tenants', # mandatory
    
    'niche', # you must list the app where your tenant model resides in
    'django.contrib.contenttypes',
    # everything below here is optional
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    
    "widget_tweaks",
    'django_celery_beat',
    'django_celery_results',
)

TENANT_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    # your tenant-specific apps    'django.contrib.messages'
    'newsletter',
)
INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

TENANT_MODEL = "niche.Niche" # app.Model
TENANT_DOMAIN_MODEL = "niche.Domain" # app.Model
PUBLIC_SCHEMA_URLCONF = "niche.urls"

SITE_ID = 1

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': "digest-newsletter",
        'USER': "oseni",
        'PASSWORD': "postgres",
        'HOST': "localhost",
        'PORT': 5432,
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static",]

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# NEWSLETTER CONFIGURATION
NEWSLETTER_EMAIL_BATCH_WAIT = 0
NEWSLETTER_EMAIL_BATCH_SIZE = 0
NEWSLETTER_SITE_BASE_URL = "http://127.0.0.1:8000"
NEWSLETTER_SUBSCRIPTION_REDIRECT_URL = reverse_lazy('newsletter:thank-you')
NEWSLETTER_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
NEWSLETTER_SNOOZE_INTERVAL = 30
NEWSLETTER_SEND_VERIFICATION = False

# EMAIL CONFIRMATION
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST_USER = "example@gmail.com"

#-----------------------------------
# REDIS DEFINITION 
#-----------------------------------
REDIS_URL = f'{os.environ.get("REDIS_URL", default="redis://127.0.0.1:6379")}/{0}'


#-----------------------------------
# CELERY DEFINITION 
#-----------------------------------
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
# this allows you to schedule items in the Django admin.
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

CELERY_CACHE_BACKEND = 'default'

# django setting.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}