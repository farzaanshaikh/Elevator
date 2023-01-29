FROM ubuntu:22.04
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore
RUN apt-get update -y
RUN apt-get install python3 python3-pip libpq-dev -y
RUN mkdir -p /myapps/elevator/
COPY ./elevator/requirements.txt /myapps/elevator/
RUN pip3 install -r /myapps/elevator/requirements.txt
COPY . /myapps
RUN ["chmod", "+x", "/myapps/entrypoint.sh"]
WORKDIR /myapps/elevator