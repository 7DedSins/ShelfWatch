import environ

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
env = environ.Env()
env.read_env(BASE_DIR / ".env")
SECRET_KEY = env("SECRET_KEY")
FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY")
# Broker for a real worker. Tests override this; daily laptop loop does not run Redis.
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
