FROM python:3.9

WORKDIR usr/src/flaskr

COPY requirements.txt .
RUN apt-get update
RUN apt-get install -y libpq-dev ffmpeg
RUN pip install --no-cache-dir -r requirements.txt
COPY . .