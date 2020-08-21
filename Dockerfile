FROM ubuntu:20.04

LABEL maintainer="frank@laatjehacken.nl"

RUN apt-get update -y && \
    apt-get install -y python3-dev python3-pip libpq-dev build-essential libsasl2-dev libldap2-dev libssl-dev

# RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

# ENTRYPOINT [ "python3" ]

ENV FLASK_APP=api.py
EXPOSE 5000

CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0" ]