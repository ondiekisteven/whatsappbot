
FROM python:3.9

WORKDIR /home/app

ENV FLASK_APP app.py

ENV FLASK_RUN_HOST 0.0.0.0

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        libxml2-dev \
        libxslt-dev \
        ffmpeg \
        python3-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt  requirements.txt

RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . .
