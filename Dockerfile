# syntax=docker/dockerfile:1
FROM ubuntu:22.04
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore
RUN apt-get update -y
RUN apt-get install python3 python3-pip libpq-dev -y
COPY . /myapps
WORKDIR /myapps/elevator
RUN pip3 install -r requirements.txt