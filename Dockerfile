FROM python:slim

RUN useradd coursemanager

WORKDIR /home/coursemanager

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY app.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP app.py

RUN chown -R coursemanager:coursemanager ./
USER coursemanager

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]