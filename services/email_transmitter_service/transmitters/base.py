import abc
import os
import json
from utils.log_config import logger

class Transmitter(abc.ABC):
    def __init__(self):
        """
        Validate config for provider and configure credentials.
        """
        self.config = self.read_config()
        self.validate_config()
        self.configure_provider()

    @staticmethod
    def read_config():
        config_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
        with open(config_filepath, 'r') as fp:
            return json.load(fp)
        
    def get_provider_config(self):
        for configuration in self.config['configurations']:
            if configuration['provider'] == self.identifier:
                return configuration

    def validate_config(self):
        self.configured_providers = [configuration['provider'] for configuration in self.config['configurations']]
        if self.identifier not in self.configured_providers:
            raise Exception(f"Please add a configuration for {self.identifier} provider in config.json file.")
        for event, mapping in self.config['events'].items():
            if not mapping.get('id', {}).get(self.identifier):
                raise Exception(f"Template ID for provider {self.identifier} corresponding to event {event} not found. " +
                                f"Please run `python setup_templates.py <stage>` to create/update templates to configured " +
                                f"providers and update them in config.json automatically.")

    @abc.abstractmethod
    def configure_provider(self):
        pass

    @abc.abstractmethod
    def handle_event(self, event, event_data, to_email_addresses):
        logger.info(f"handle_event received by {self.identifier} transmitter. " +
                    f"event: {event}, event_data: {event_data}, to_email_addresses: {to_email_addresses}")

        # Always read fresh config before handling event to avoid restarting service after every change.
        self.config = self.read_config()

        event_mapping = self.config['events'].get(event)
        if not event_mapping:
            raise Exception(f'Received event {event} not configured in config.json. Ignoring event...')
