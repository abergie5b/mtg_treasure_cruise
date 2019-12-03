FROM python:3.6

ADD . /treasure_cruise
WORKDIR /treasure_cruise

RUN pip install -no-cache-dir -r requirements.txt

ENTRYPOINT "./entrypoint.sh"
