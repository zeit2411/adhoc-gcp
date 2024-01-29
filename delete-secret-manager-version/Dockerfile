ARG PYTHON_VERSION=3.9-slim-buster
FROM python:${PYTHON_VERSION} as python

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

ADD requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

ADD config.json ./config.json
ADD main.py ./main.py

CMD tail -f /dev/null