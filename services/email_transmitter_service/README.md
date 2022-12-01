# E-mail Transmitter Service
This is the standard email transmitter service that supports SES and Mailjet


## Configuration

Follow the following steps to configure the E-mail transmitter service.

### 1. Configuration file

1.1. Copy the `.env.example` file as `.env` and fill the variables or run `run.sh` script from the root `services` directory.

- `ROLLBAR_ACCESS_TOKEN`: Project access token of a Rollbar project.
- `BROKER_PATH`: Path to RabbitMQ broker. E.g. `rabbitmq:5672`
- `EMAIL_PROVIDER`: The e-mail service provider to use: `mailjet` and `ses` are currently supported.


1.2. Fill in the `config.json` file according to the existing file.

```json
{
    "configurations": [
        {
            "provider": "ses",
            "sourceEmail": "TemplateProject <template@asymlabs.net>",
            "accessKeyId": "AQJAxxxxxxxxxxxxx",
            "accessKeySecret": "iPN5Qxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "region": "us-west-2"
        },
        {
            "provider": "mailjet",
            "publicApiKey": "cd8fxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "privateApiKey": "bb48xxxxxxxxxxxxxxxxxxxxxxxxx",
            "sourceEmail": "TemplateProject <template@asymlabs.net>",
            "errorReportingEmail": "asymlabs@gmail.com"
        },
        // ... more configurations
    ],
    "events": {
        "USER_CREATED": {
            "subject": "Welcome {{var:recipient_name}}",
            "templateName": "Welcome"
        },
        // ... more events
    }
}
```

- `configurations`: The `configurations` array contains a list of configured providers. The supported  
configuration variables for each provider are specified in the example above.
- `events`: The `events` object contains a list of events that should be handled by the e-mail transmitter
service. The `templateName` variable refers to the HTML template file that should be present in the `templates` directory.

### 2. Set up templates

After configuration, the next step is to upload templates to each provider. To do that, you can run 
`python setup_templates.py <stage>` which does the following:
- Upload all event templates to each provider configured in `config.json`.
- Update the `config.json` file with the ID of each uploaded template. I.e. after running 
`setup_templates.py` each event will have an additional `id` object which looks like this:
```json
"USER_CREATED": {
    "subject": "Welcome {{var:recipient_name}}",
    "templateName": "Welcome",
    "id": {
        "ses": "ProjectName-Welcome-asim",
        "mailjet": 4286015
    }
}
```

**Note**: The template HTML files in `templates` directory should contain only the HTML part of the email
and variables in the following format: `{{var:variable_name}}`.


### 3. Triggering E-mail transmitter.

The e-mail transmitter service expects messages in the following format:
```json
{
    "event": "<event_name>",
    "data": {
        "variable": "data"
    },
    "to_emails": [
        "recipient@email.com"
    ]
}
```

- The provider to be used is to send the e-mail is determined by `EMAIL_PROVIDER` environment variable.
- The template to be used is determined by `event.id` object which contains the template ID for each configured provider.



## Development

To add support for a new provider, add another class in `transmitters` directory that inherits from `Transmitter` class in `transmitters/base.py`. The new `ProviderTransmitter` class must implement the following two methods at least:
- `configure_provider`
- `handle_event`
