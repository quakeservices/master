FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /usr/src/app/

CMD [ "python3", "app.py" ]
