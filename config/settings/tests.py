from .base import *

DEBUG = False
SECRET_KEY = "test-not-secret"
FIELD_ENCRYPTION_KEY = "VaRvsu7p1TLo44iB9HTS90w1bAuMtBMLcnV4aCjiPAU="
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
# Eager: .delay() runs in-process. Proves Python, not Redis/Beat/serialization.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
# Eager still constructs a Celery app; a dummy URL avoids a missing-broker surprise.
CELERY_BROKER_URL = "memory://"
