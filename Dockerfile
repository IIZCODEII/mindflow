FROM python:3.7-slim-stretch

RUN apt-get update && apt-get install -y git python3-dev gcc \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update ##[edited]

RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements.txt .

RUN python -m ensurepip --upgrade

RUN python -m pip install --upgrade setuptools

RUN pip install --upgrade -r requirements.txt

COPY app app/

EXPOSE 5000

CMD ["python", "app/server.py", "serve"]