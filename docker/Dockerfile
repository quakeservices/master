# syntax=docker.io/docker/dockerfile:1
# vim:set ft=dockerfile:

# +++++++++++++++
#     Base
# +++++++++++++++
FROM python:3.12-slim AS base

ARG CODE_DIR="/opt/quakeservices"
ARG PIP_VERSION
ARG POETRY_VERSION
ENV PIP_ROOT_USER_ACTION=ignore

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN mkdir -p $CODE_DIR

WORKDIR $CODE_DIR

COPY pyproject.toml poetry.lock $CODE_DIR/

RUN python -m pip install \
      --no-cache-dir \
      "pip==$PIP_VERSION" \
      "poetry==$POETRY_VERSION"

# +++++++++++++++
#     Master
# +++++++++++++++

FROM base AS master

# hadolint ignore=DL4006
RUN poetry export --format=requirements.txt \
                  --without-hashes \
                  --with main,master \
  | pip install --no-cache-dir \
                --requirement /dev/stdin

COPY master $CODE_DIR/master
COPY qs.py $CODE_DIR

CMD [ "/opt/quakeservices/qs.py", \
      "--log-level", "debug", \
      "--hide-boto-logs", \
      "server", \
      "run"]
