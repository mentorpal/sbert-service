# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/configure.html#configuration-file
# https://docs.gunicorn.org/en/stable/settings.html
import multiprocessing

# https://docs.gunicorn.org/en/stable/settings.html#workers
workers = multiprocessing.cpu_count() * 2 + 1

# limit max clients at the time to prevent overload:
worker_connections=150

# needs ip set or will be unreachable from host
# regardless of docker-run port mappings
bind="0.0.0.0:5000"

# to prevent any memory leaks:
max_requests = 1000
max_requests_jitter = 50
