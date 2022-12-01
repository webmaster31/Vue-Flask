


import os
import sys
import json
import re


PROJECT_NAME = "ProjectName"


def mailjet_variables_to_ses_variable(template_string):
    return re.sub(r"{{var:(.*?)}}", r"{{\1}}", template_string)


def create_or_update_ses_template(template_filepath, template_name, subject, access_key, key_secret, region, stage):
    from botocore.exceptions import ClientError
    import boto3
    ses = boto3.client(
        'ses', 
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=key_secret,
    )

    subject = mailjet_variables_to_ses_variable(subject)

    with open(template_filepath, 'r') as template_file:
        template_html = template_file.read()
    template_html = mailjet_variables_to_ses_variable(template_html)
    template_obj = {'TemplateName': template_name, 'TextPart': '', 'SubjectPart': subject, 'HtmlPart': template_html}

    if not template_obj['TemplateName'].endswith('-' + stage):
        template_obj['TemplateName'] = template_obj['TemplateName'] + '-' + stage

    try:
        ses.create_template(Template=template_obj)
    except ClientError as e:
        if e.response['Error']['Code'] == 'AlreadyExists':
            ses.update_template(Template=template_obj)
        else:
            print("Unexpected error: %s" % e)


def create_or_update_mailjet_template(template_filepath, template_name, subject, api_key, api_secret, stage):
    from mailjet_rest import Client
    mailjet = Client(auth=(api_key, api_secret), version='v3')
    with open(template_filepath) as html_file:
        html = html_file.read()

        # Append stage name if not appended
        if not template_name.endswith('-' + stage):
            template_name = template_name + '-' + stage
        
        # Create mailjet template
        data = {
            "Author": "upload_templates.py",
            "Name": template_name,
            "OwnerType": "apikey",
            "Purposes": ["transactional"]
        }

        response = mailjet.template.create(data=data)
        already_exists = False
        
        if response.ok:
            print("Template created successfully...")
            res_json = response.json()
            template_id = res_json['Data'][0]['ID']
        else:
            res_json = response.json()
            if "already exists" in res_json.get("ErrorMessage", "").lower():
                already_exists = True
                print("Template already exists. Skipping creation...")
            else:
                print("An error occurred while creating a template:")
                print(res_json)
                return False
        
        if already_exists:
            response = mailjet.template.update(id="apiKey|" + template_name, data=data)
            if response.ok:
                res_json = response.json()
                template_id = res_json['Data'][0]['ID']
                print("Template updated successfully...")
            else:
                res_json = response.json()
                print("An error occurred while updating a template:")
                print(res_json)
                return False

        # Create mailjet template content
        data = {
            "Headers": {
                "Subject": subject
            },
            "Html-part": html
        }
        response = mailjet.template_detailcontent.create(id="apiKey|" + template_name, data=data)
        already_exists = False

        if response.ok:
            print("Template content added successfully...")
        else:
            try:
                res_json = response.json()
                if "already exists" in res_json.get("ErrorMessage", "").lower():
                    already_exists = True
                    print("Template content already exists. Skipping creation...")
                else:
                    print("An error occurred while creating a template:")
                    print(res_json)
            except Exception as e:
                print("Unexpecetd error")
                print(e)
                print(response.text)
            return False
        
        if already_exists:
            response = mailjet.template_mailcontent.update(id="apiKey|" + template_name, data=data)
            if response.ok:
                print("Template content updated successfully...")
            else:
                res_json = response.json()
                print("An error occurred while updating a tempalte content:")
                print(res_json)
                return False
        return template_id


def run(stage):
    config_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    with open(config_filepath, 'r') as f:
        global_config = json.loads(f.read())

    for configuration in global_config['configurations']:
        provider = configuration.get('provider')
        if provider == 'mailjet':
            # Do mailjet stuff
            print()
            print("Configuring Mailjet provider:")
            mj_api_key = configuration["publicApiKey"]
            mj_api_secret = configuration["privateApiKey"]
            for _, template in global_config['events'].items():
                template_filepath = os.path.join(templates_dir, template['templateName'] + '.html')
                if not os.path.exists(template_filepath):
                    print(f"Unable to find template file for {template['templateName']} at {template_filepath}")
                    sys.exit(1)
                template_name = PROJECT_NAME + "-" + template['templateName'] + f"-{stage}"
                template_id = create_or_update_mailjet_template(
                    template_filepath, 
                    template_name, 
                    template['subject'], 
                    mj_api_key, 
                    mj_api_secret, 
                    stage
                )
                template['id'] = template.get('id') or {}
                template['id'][provider] = template_id
        elif provider == 'ses':
            # Do ses stuff
            print()
            print("Configuring SES provider:")
            aws_access_key_id = configuration.get("accessKeyId") or os.getenv('AWS_ACCESS_KEY_ID')
            aws_access_key_secret = configuration.get("accessKeySecret") or os.getenv('AWS_ACCESS_KEY_SECRET')
            aws_region = configuration.get("region") or os.getenv('AWS_REGION')
            for _, template in global_config['events'].items():
                template_filepath = os.path.join(templates_dir, template['templateName'] + '.html')
                if not os.path.exists(template_filepath):
                    print(f"Unable to find template file for {template['templateName']} at {template_filepath}")
                    sys.exit(1)
                template_name = PROJECT_NAME + "-" + template['templateName'] + f"-{stage}"
                create_or_update_ses_template(
                    template_filepath, 
                    template_name, 
                    template['subject'], 
                    aws_access_key_id, 
                    aws_access_key_secret, 
                    aws_region, 
                    stage
                )
                template['id'] = template.get('id') or {}
                template['id'][provider] = template_name
        else:
            print("Invalid provider specified in configurations: {}".format(provider))
            
    with open(config_filepath, 'w+') as fp:
        json.dump(global_config, fp, indent=4)


if __name__ == '__main__':
    import sys

    args = sys.argv
    if len(args) >= 2:
        stage_name = args[1]

        os.environ['STAGE'] = stage_name

        success = run(stage=stage_name)

        if not success:
            sys.exit(1)
    else:
        print("Missing stage argument. Usage: python update_email_templates.py <stage>")
