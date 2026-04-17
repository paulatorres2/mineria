import os

# Bind
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Workers
workers = int(os.environ.get("WEB_CONCURRENCY", 2))

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
