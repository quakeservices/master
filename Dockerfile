FROM python:3-alpine

RUN apk --no-cache add geoip geoip-dev gcc musl-dev libmaxminddb

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
