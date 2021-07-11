FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN --mount=type=cache,target=/root/.cache/pip \
  pip install --upgrade pip

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
  pip install -r requirements.txt

COPY . /usr/src/app/

CMD [ "python3", "app.py" ]
