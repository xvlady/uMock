FROM docker-mf-base.unixrepo.megafon.ru/universal-base-images/python:3.8-ubi8
USER root

ENV HOME=/app/ \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LANG=en_US.UTF-8 \
    LD_LIBRARY_PATH="/usr/local/lib"

COPY conf/main.ini /conf/

COPY app/Pipfile.lock /app/

RUN echo "/venv" > /app/.venv

RUN cd /app &&  \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipenv==2018.11.26 && \
    pipenv install --ignore-pipfile && \
    pipenv install --ignore-pipfile uwsgi==2.0.18

COPY nltk_data /nltk_data

COPY app/ /app/
RUN mkdir -p /app/tmp /app/media /app/log

RUN groupadd docker && groupmod -g 991 docker && \
    adduser ansible && usermod -u 54297 -aG docker ansible && \
    chown -R 54297:54297 /app /conf

WORKDIR /app
ENTRYPOINT bash --login -c 'pipenv run wog_start'

ARG VERSION
ENV VERSION $VERSION
