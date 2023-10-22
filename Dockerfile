# syntax=docker.io/docker/dockerfile:1
# vim:set ft=dockerfile:

FROM python:3.12-slim as base

ARG POETRY_VERSION
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /tmp

COPY pyproject.toml poetry.lock .

RUN python -m pip install -U pip setuptools \
 && python -m pip install "poetry==$POETRY_VERSION"

# +++++++++++++++
#     Master
# +++++++++++++++

FROM base as master

RUN poetry export --format=requirements.txt \
                  --without-hashes \
                  --with main,master \
  | pip install -r /dev/stdin

WORKDIR /opt/quakeservices

COPY master /opt/quakeservices/master
COPY qs.py /opt/quakeservices

CMD [ "/opt/quakeservices/qs.py", \
      "--log-level", "debug", \
      "--hide-boto-logs", \
      "server", \
      "run"]

# +++++++++++++++
#     CDK
# +++++++++++++++

FROM base as cdk

ARG CDK_CLI_VERSION

ARG DOCKER_STATIC_VERSION="24.0.6"
ARG DOCKER_STATIC_ARCH="x86_64"
ARG DOCKER_STATIC_URL="https://download.docker.com/linux/static/stable/$DOCKER_STATIC_ARCH/docker-$DOCKER_STATIC_VERSION.tgz"
ARG DOCKER_STATIC_PATH="/tmp/docker-$DOCKER_STATIC_VERSION.tgz"
ARG DOCKER_STATIC_BIN_DIR="/usr/bin/"

ARG NODE_MAJOR="20"
ARG NODE_GPG_PATH="/etc/apt/keyrings/nodesource.gpg"
ARG NODE_GPG_URL="https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key"
ARG NODE_REPO_URL="https://deb.nodesource.com/node_$NODE_MAJOR.x"
ARG NODE_REPO_PATH="/etc/apt/sources.list.d/nodesource.list"
ARG NODE_REPO_CONTENT="deb [signed-by=$NODE_GPG_PATH] $NODE_REPO_URL nodistro main"

RUN apt-get update -y  \
 && apt-get install -y --no-install-recommends \
      curl \
 && curl --fail \
         --silent \
         --show-error \
         --location \
         --output $DOCKER_STATIC_PATH \
         $DOCKER_STATIC_URL \
 && tar --extract \
        --strip-components 1 \
        --file $DOCKER_STATIC_PATH \
        --directory /usr/bin \
        docker/docker \
 && apt-get clean \
 && rm -rf $DOCKER_STATIC_PATH

RUN mkdir -p /etc/apt/keyrings \
  && apt-get update \
  && apt-get install --no-install-recommends -y \
       ca-certificates \
       gnupg \
       curl \
 && curl -fsSL $NODE_GPG_URL \
  | gpg --dearmor -o $NODE_GPG_PATH \
 && echo $NODE_REPO_CONTENT > $NODE_REPO_PATH \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      nodejs \
 && apt-get clean

RUN npm install --global aws-cdk@$CDK_CLI_VERSION

RUN poetry export --format=requirements.txt \
                  --without-hashes \
                  --with main,cdk \
  | pip install -r /dev/stdin

# +++++++++++++++
#     Test
# +++++++++++++++

FROM cdk as test

RUN poetry export --format=requirements.txt \
                  --without-hashes \
                  --with dev,master \
  | pip install -r /dev/stdin

# +++++++++++++++
#     Docs
# +++++++++++++++

FROM cdk as docs

RUN npm install --global prettier@latest

RUN poetry export --format=requirements.txt \
                  --without-hashes \
                  --with docs,master \
  | pip install -r /dev/stdin
