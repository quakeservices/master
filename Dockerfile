FROM python:3-alpine

RUN apk --no-cache add geoip geoip-dev gcc musl-dev libmaxminddb

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip install --upgrade pip
RUN pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app/

ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
