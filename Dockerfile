FROM python:3.10-slim
WORKDIR /app/
ENV FLASK_APP=server
ENV PYTHONPATH /app
ENV SHARED_ROOT /app/shared 
# ENV PATH="/app/bin:${PATH}"

COPY entrypoint.sh ./
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

# if we just copy these 2 files, docker cache should reuse installation layers
COPY pyproject.toml poetry.lock ./
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
# sentence-transformers require git installed:
RUN apt-get update && apt-get install -y git
RUN poetry install --no-dev --no-root
RUN apt-get purge -y git
# force delete poetry and pip caches
RUN rm -rf /root/.cache/*
# TODO this leaves all poetry pip dependencies installed
RUN pip uninstall -y poetry virtualenv pyparsing

COPY shared/installed /app/shared
COPY server ./server
