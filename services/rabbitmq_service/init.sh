#!/bin/sh

# Create Rabbitmq user
( rabbitmqctl wait --timeout 60 "$RABBITMQ_PID_FILE" ; \
rabbitmqctl add_user "$RABBITMQ_USER" "$RABBITMQ_PASSWORD" 2>/dev/null ; \
rabbitmqctl set_user_tags "$RABBITMQ_USER" administrator ; \
rabbitmqctl add_vhost "$RABBITMQ_VHOST" ; \
rabbitmqctl set_permissions -p "$RABBITMQ_VHOST" "$RABBITMQ_USER"  ".*" ".*" ".*" ; \
echo "*** User '$RABBITMQ_USER' with password '$RABBITMQ_PASSWORD' completed. ***") &

# $@ is used to pass arguments to the rabbitmq-server command.
# For example: docker run -d rabbitmq arg1 arg2,
# it will be same as running in the container rabbitmq-server arg1 arg2
rabbitmq-server "$@"
