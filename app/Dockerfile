###########
# BUILDER #
###########

# pull official base image
FROM python:3

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# lint
RUN pip install --upgrade pip

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt
