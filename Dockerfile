FROM python:3

# libgammu-dev needed by https://github.com/gammu/python-gammu/issues/32
RUN apt-get update && apt-get install -y \
    pkg-config \
    gammu \
    libgammu-dev

RUN mkdir ssl

ENV BASE_PATH /sms-gw
RUN mkdir $BASE_PATH
WORKDIR $BASE_PATH
ADD requirements.txt .
ADD gammu.config .
ADD credentials.txt .
ADD support.py .

RUN pip install -r requirements.txt

ADD run.py .

CMD [ "python", "./run.py" ]
