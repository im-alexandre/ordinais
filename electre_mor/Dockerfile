###########
# BUILDER #
###########

# pull official base image
FROM python:3.13.0

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# lint
RUN pip install --upgrade pip

# install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

