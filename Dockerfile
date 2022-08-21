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
COPY course-manager.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP course-manager.py

RUN chown -R coursemanager:coursemanager ./
USER coursemanager

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]