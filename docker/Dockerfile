# syntax=docker.io/docker/dockerfile:1
# vim:set ft=dockerfile:

FROM python:3.12-slim AS base

ARG PIP_VERSION
ARG POETRY_VERSION
ENV PIP_ROOT_USER_ACTION=ignore

RUN mkdir -p $CODE_DIR

WORKDIR $CODE_DIR

COPY pyproject.toml poetry.lock .

RUN python -m pip install \
      "pip==$PIP_VERSION" \
      "poetry==$POETRY_VERSION"

# +++++++++++++++
#     Master
# +++++++++++++++

FROM base AS master

ARG CODE_DIR="/opt/quakeservices"

RUN poetry export --format=requirements.txt \
                  --without-hashes \
                  --with main,master \
  | pip install -r /dev/stdin


COPY master $CODE_DIR/master
COPY qs.py $CODE_DIR

CMD [ "/opt/quakeservices/qs.py", \
      "--log-level", "debug", \
      "--hide-boto-logs", \
      "server", \
      "run"]
