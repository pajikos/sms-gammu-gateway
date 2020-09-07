FROM python:3-alpine

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.9/community' >> /etc/apk/repositories
RUN apk update
RUN apk add --no-cache pkgconfig gammu=1.39.0-r2 gammu-libs=1.39.0-r2  gammu-dev=1.39.0-r2
RUN mkdir ssl

ENV BASE_PATH /sms-gw
RUN mkdir $BASE_PATH
WORKDIR $BASE_PATH
ADD requirements.txt .
ADD gammu.config .
ADD credentials.txt .
ADD support.py .

#RUN pip install -r requirements.txt

RUN apk add --no-cache --virtual .build-deps libffi-dev openssl-dev gcc musl-dev \
     && pip install -r requirements.txt \
     && apk del .build-deps libffi-dev openssl-dev gcc musl-dev

ADD run.py .

CMD [ "python", "./run.py" ]
