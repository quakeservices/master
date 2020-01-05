FROM python:3-alpine

RUN apk --no-cache add geoip geoip-dev gcc musl-dev libmaxminddb

COPY ./nonfree/GeoLite2-City.mmdb /var/lib/libmaxminddb/GeoLite2-City.mmdb

RUN ln -s /var/lib/libmaxminddb/GeoLite2-City.mmdb /usr/share/GeoIP/GeoIP.dat

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./app.py"]
