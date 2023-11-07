FROM python:3.10

COPY . /adbot
WORKDIR /adbot

RUN apt-get update \
    && pip3 install --upgrade pip \
    && pip3 install --upgrade setuptools \
    && pip3 install -r requirements.txt
RUN chmod 755 .
