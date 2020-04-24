FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /opt/translateforsg/backend
WORKDIR /opt/translateforsg/backend

RUN pip install uwsgi
RUN pip install grpcio==1.28.1

COPY requirements.txt /opt/translateforsg/backend/

RUN pip install -r requirements.txt

COPY . /opt/translateforsg/backend/

EXPOSE 80
CMD uwsgi --http :80 --module translateforsg.wsgi --enable-threads
