FROM python:3

ENV PYTHONUNBUFFERED 1
ENV DEBUG 1
ENV SECRET_KEY docker

RUN mkdir /code

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt
