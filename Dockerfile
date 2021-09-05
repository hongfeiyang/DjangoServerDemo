FROM python:3.9
ENV PYTHONUUNBUFFERED=1
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt