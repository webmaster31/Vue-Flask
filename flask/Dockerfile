FROM python:3.9-alpine

RUN apk update &&  \
            apk add gcc build-base libc-dev make git libffi-dev openssl-dev python3-dev libxml2-dev libxslt-dev  \
            jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
# Since Flask apps listen to port 5000  by default, we expose it
EXPOSE 5000

# Sets the working directory for following COPY and CMD instructions
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY ./requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir

COPY . /app

# Run main.py when the container launches
ENV FLASK_APP main.py
ENTRYPOINT ["./docker-entrypoint.sh"]

