FROM python:3-alpine

RUN apk --no-cache add geoip geoip-dev gcc musl-dev libmaxminddb

RUN touch /var/lib/libmaxminddb/GeoLite2-City.mmdb && \
    ln -s /var/lib/libmaxminddb/GeoLite2-City.mmdb /usr/share/GeoIP/GeoIP.dat

RUN /etc/periodic/weekly/libmaxminddb

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./app.py"]
