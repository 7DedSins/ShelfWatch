import environ

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
env = environ.Env()
env.read_env(BASE_DIR / ".env")
SECRET_KEY = env("SECRET_KEY")
FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
