import json
import os

from mailjet_rest import Client


def send_custom_email(message):
    """
    :param message: dict: {
        'email_data': {
            'email_type': str,
            'recipient_email': str,
            'recipient_name': str,
            'subject': str,
            'confirmation_link': str,
            'password_reset_url': str
        }
    }
    :return:
    """
    api_key = os.environ['MJ_APIKEY_PUBLIC']
    api_secret = os.environ['MJ_APIKEY_PRIVATE']
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    email_data = message.get('email_data')
    email_type = email_data.get('email_type')
    template_id = os.environ.get(email_type.upper())
    data = {
        'Messages': [
            {
                "From": {
                    "Email": os.environ.get('SENDER_EMAIL'),
                    "Name": os.environ.get('SENDER_NAME')
                },
                "To": [
                    {
                        "Email": email_data.get('recipient_email'),
                        "Name": email_data.get('recipient_name')
                    }
                ],
                "TemplateID": int(template_id),
                "TemplateLanguage": True,
                "Subject": email_data.get('subject'),
                "Variables": {
                    "recipient_name": email_data.get('recipient_name'),
                    "confirmation_link": email_data.get('confirmation_link'),
                    "company_name": os.environ.get('COMPANY_NAME'),
                    "password_reset_url": email_data.get("password_reset_url")
                }
            }
        ]
    }
    print(f"SEND EMAIL WITH DATA: {json.dumps(data)}")
    return mailjet.send.create(data=data)


if __name__ == '__main__':
    # set the given data before running this file for email test
    data = {
        'email_data': {
            'email_type': '',
            'recipient_email': '',
            'recipient_name': '',
            'subject': '',
            'confirmation_link': '',
            'password_reset_url': ''
        }
    }
    print(send_custom_email(data))
