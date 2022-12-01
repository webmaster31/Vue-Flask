import os
import json
import boto3
from botocore.exceptions import ClientError

from transmitters.base import Transmitter
from utils.log_config import logger

class SesTransmitter(Transmitter):
    identifier = 'ses'

    def configure_provider(self):
        configuration = self.get_provider_config()
        aws_access_key_id = configuration.get("accessKeyId") or os.getenv('AWS_ACCESS_KEY_ID')
        aws_access_key_secret = configuration.get("accessKeySecret") or os.getenv('AWS_ACCESS_KEY_SECRET')
        aws_region = configuration.get("region") or os.getenv('AWS_REGION')
        if not aws_access_key_id or not aws_access_key_secret or not aws_region:
            raise Exception("AWS Access Key ID, Secret Access Key, or region not found in config.json or environment variables.")
        self.transmitter_source = configuration.get("sourceEmail")
        if not self.transmitter_source:
            raise Exception("sourceEmail not found in ses configuration in config.json.")
        self.client = boto3.client(
            'ses',
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_access_key_secret,
        )

    def handle_event(self, event, event_data, to_email_addresses):
        super().handle_event(event, event_data, to_email_addresses)
        event_mapping = self.config['events'][event]
        try:
            response = self.client.send_templated_email(
                Destination={
                    'ToAddresses': to_email_addresses
                },
                Template=event_mapping['id'][self.identifier],
                TemplateData=json.dumps(event_data),
                Source=self.transmitter_source
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            logger.error(e.response['Error']['Message'])
        else:
            logger.debug("Email sent! Message ID:"),
            logger.debug(response['MessageId'])

