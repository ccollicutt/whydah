# Dockerfile
FROM python:3.11-slim
RUN apt update && apt install -y git
COPY requirements.txt /
RUN set -ex && \
    pip install -r requirements.txt
ADD whydah /app/whydah
RUN pip install gunicorn
COPY gunicorn-run.sh /app/
RUN useradd gunicorn -u 10001 --user-group
USER 10001
WORKDIR /app

ENTRYPOINT [ "/app/gunicorn-run.sh" ]