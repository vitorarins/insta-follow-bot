FROM phusion/baseimage:latest
MAINTAINER Vitor Arins <vitorarins@gmail.com>

RUN apt-get update
RUN apt-get install -y python python-pip python-dev gcc
RUN pip install flask flask-socketio python-instagram

RUN mkdir -p /docker/app
ADD ./templates/ /docker/app/templates
ADD ./app.py /docker/app/app.py

WORKDIR /docker/app

EXPOSE 80
CMD ["python", "app.py"]