import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production')

DEBUG = os.environ.get('DJANGO_DEBUG', '1') in ('1', 'true', 'True', 'yes', 'YES')

_allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
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

ROOT_URLCONF = 'football_project.urls'

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
                'core.context_processors.admin_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'football_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# === XAVFSIZLIK ===

# Fayl yuklash chegaralari (suiiste'moldan himoya)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB form ma'lumotlari uchun
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024    # 5 MB bir fayl uchun (xotirada)
DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000              # POST form maydonlari soni

# HTTP xavfsizlik sarlavhalari (hamma muhitda)
SECURE_CONTENT_TYPE_NOSNIFF = True               # MIME sniffing'ni bloklash
SECURE_REFERRER_POLICY = 'same-origin'           # Referer'ni faqat o'z domen'da yuborish
X_FRAME_OPTIONS = 'DENY'                          # iframe'ga joylashni butunlay taqiqlash (clickjacking)
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Cookie xavfsizligi
SESSION_COOKIE_HTTPONLY = True                    # JS orqali cookie'ga kirish taqiq
SESSION_COOKIE_SAMESITE = 'Lax'                   # CSRF himoyasini kuchaytirish
CSRF_COOKIE_SAMESITE = 'Lax'

# Session
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7             # 1 hafta (default 2 hafta — qisqartiramiz)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Brute-force himoyasi uchun cache (LocMem default)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'e-futbol-cache',
    }
}

# Login chegaralari (brute-force himoyasi)
LOGIN_RATE_LIMIT_ATTEMPTS = 5                     # 5 ta urinishdan keyin
LOGIN_RATE_LIMIT_WINDOW = 15 * 60                 # 15 daqiqa ichida
LOGIN_RATE_LIMIT_LOCKOUT = 30 * 60                # 30 daqiqa bloklash

# Production rejimida (DEBUG=False) faqat HTTPS uchun
if not DEBUG:
    SECURE_SSL_REDIRECT = True                    # HTTP → HTTPS yo'naltirish
    SESSION_COOKIE_SECURE = True                  # Cookie faqat HTTPS orqali
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000                # 1 yil (HSTS)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
