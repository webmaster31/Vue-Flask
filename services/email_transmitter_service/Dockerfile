FROM python:3.9-alpine

WORKDIR /src

RUN apk update &&  \
    apk add gcc build-base libffi-dev

COPY ./requirements.txt /src
RUN pip install -r requirements.txt

RUN export PYTHONPATH=$PYTHONPATH:$(pwd)
COPY ./ /src

RUN chmod +x /src/docker-entrypoint.sh
# production
ENTRYPOINT ["./docker-entrypoint.sh"]
