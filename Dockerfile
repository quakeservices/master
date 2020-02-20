FROM python:3-alpine

RUN apk --no-cache add geoip geoip-dev gcc musl-dev libmaxminddb

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN --mount type=volume,source=pip-cache,target=/root/.cache/pip pip install --upgrade pip
RUN --mount type=volume,source=pip-cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .

CMD ["python", "./app.py"]
