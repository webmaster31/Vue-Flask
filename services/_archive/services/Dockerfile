FROM python:3.9-alpine

WORKDIR /queue

RUN apk update &&  \
    apk add gcc build-base libffi-dev

COPY ./requirements.txt /queue
RUN pip install -r requirements.txt

RUN export PYTHONPATH=$PYTHONPATH:$(pwd)
COPY ./ /queue

# production
ENTRYPOINT ["./docker-entrypoint.sh"]
