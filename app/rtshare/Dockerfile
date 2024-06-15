# Dockerfile for the RTSahre App
#
# Installs the Django App, and runs it with Gunicorn
#
# author: Brian Schrader
# since: 2022-03-21

FROM  python:3.12
MAINTAINER Brian Schrader <brian@brianschrader.com>
EXPOSE 8000
WORKDIR app

# Install Required Dependencies
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Cache requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
