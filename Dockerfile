FROM python:3-alpine

RUN apk --no-cache add geoip geoip-dev gcc musl-dev

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./app.py", "--debug"]
