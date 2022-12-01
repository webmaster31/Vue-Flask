#!/bin/ash

if [ ! -d "/root/.aws" ]
then
    mkdir /root/.aws
fi

if [ ! -f /root/.aws/credentials ]; then
	touch /root/.aws/credentials
	touch /root/.aws/config

	echo "[default]\n\
			aws_access_key_id = ${AWS_ACCESS_KEY_ID}\n\
			aws_secret_access_key = ${AWS_ACCESS_KEY_SECRET}" >> /root/.aws/credentials

	if [ -z "${REGION}" ]
	then
			echo "[default]\n\
					region = us-west-2" >> /root/.aws/config
	else
			echo "[default]\n\
					region = ${REGION}" >> /root/.aws/config
	fi
fi

echo "Running E-mail Transmitter..."

python3 service.py ${STAGE}
