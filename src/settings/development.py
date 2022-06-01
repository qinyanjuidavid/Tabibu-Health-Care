import os
from src.settings.local import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000"
]
