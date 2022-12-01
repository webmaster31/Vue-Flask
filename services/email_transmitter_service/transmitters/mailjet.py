import os
import re

from mailjet_rest import Client
from utils.log_config import logger
from transmitters.base import Transmitter


class MailjetTransmitter(Transmitter):
    identifier = 'mailjet'
        
    def configure_provider(self):
        configuration = self.get_provider_config()
        api_key = configuration.get("publicApiKey") or os.getenv('MJ_APIKEY_PUBLIC')
        api_secret = configuration.get("privateApiKey") or os.getenv('MJ_APIKEY_PRIVATE')
        if not api_key or not api_secret:
            raise Exception("Mailjet Public API Key or Private API Key not found in config.json or environment variables.")
        self.transmitter_source = configuration.get("sourceEmail")
        if not self.transmitter_source:
            raise Exception("sourceEmail not found in mailjet configuration in config.json.")
        self.transmitter_source = self.get_sender_data(self.transmitter_source)
        self.error_reporting_email = configuration.get("errorReportingEmail")
        self.client = Client(auth=(api_key, api_secret), version='v3.1')

    # source example: BrewOptix <a@b.com>
    @staticmethod
    def get_sender_data(source):
        match = re.match('^(.*)\s*<(.*)>$', source)
        name, email = match.groups()
        return {
            "Name": name,
            "Email": email
        }


    def handle_event(self, event, event_data, to_email_addresses):
        super().handle_event(event, event_data, to_email_addresses)
        event_mapping = self.config['events'][event]
        data = {
            'Messages': [
                {
                    "From": self.transmitter_source,
                    "To": [ { 'Email': email } for email in to_email_addresses ],
                    "TemplateLanguage": True,
                    "TemplateID": event_mapping['id'][self.identifier],
                    "Variables": event_data
                }
            ]
        }
        if self.error_reporting_email:
            data['Messages'][0]['TemplateErrorReporting'] = {
                'Email': self.error_reporting_email
            }
        
        result = self.client.send.create(data=data)
        logger.debug('Source: {}'.format(data['Messages'][0]['From']))
        logger.debug('Destination: {}'.format(data['Messages'][0]['To']))
        logger.debug('Template: {}'.format(data['Messages'][0]['TemplateID']))
        logger.debug('TemplateData: {}'.format(data['Messages'][0]['Variables']))

        logger.debug('Status Code: {}'.format(result.status_code))
        logger.debug('Response: {}'.format(result.text))
