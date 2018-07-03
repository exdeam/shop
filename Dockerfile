FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

ADD requirements.txt /app/
RUN deps="libcairo-gobject2 libpangocairo-1.0-0" \
 && build_deps="build-essential default-libmysqlclient-dev" \
 && apt-get update \
 && apt-get install -y $build_deps $deps \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y $build_deps \
 && rm -rf /var/lib/apt/lists/*
