FROM python:3-alpine AS base

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.9/community' >> /etc/apk/repositories \
    && apk update \
    && apk add --no-cache pkgconfig gammu=1.39.0-r2 gammu-libs=1.39.0-r2 gammu-dev=1.39.0-r2

# Build dependencies in a dedicated stage
FROM base AS dependencies
COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps libffi-dev openssl-dev gcc musl-dev python3-dev cargo \
    && pip install -r requirements.txt

# Switch back to base layer for final stage
FROM base AS final
ENV BASE_PATH /sms-gw
RUN mkdir $BASE_PATH /ssl
WORKDIR $BASE_PATH
COPY . $BASE_PATH

COPY --from=dependencies /root/.cache /root/.cache
RUN pip install -r requirements.txt && rm -rf /root/.cache

CMD [ "python", "./run.py" ]
