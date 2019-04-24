FROM python:3

# libgammu-dev needed by https://github.com/gammu/python-gammu/issues/32
RUN apt-get update && apt-get install -y \
    pkg-config \
    gammu \
    libgammu-dev

ADD requirements.txt /
ADD gammu.config /
ADD credentials.txt /
ADD support.py /

RUN mkdir ssl

RUN pip install -r requirements.txt

ADD run.py /

CMD [ "python", "./run.py" ]
