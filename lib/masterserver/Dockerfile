# syntax=docker/dockerfile:1
FROM quakeservices/base:latest

WORKDIR /usr/src/app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
  python3 -m pip install -r requirements.txt

COPY . /usr/src/app/

CMD [ "python3", "app.py" ]
