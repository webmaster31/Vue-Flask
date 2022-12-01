import os
import sys
import json
from dotenv import dotenv_values
from mailjet_rest import Client


def create_or_update_mailjet_template(template_filepath, template_name, api_key, api_secret, stage):
    mailjet = Client(auth=(api_key, api_secret), version='v3')
    with open(template_filepath) as html_file:
        html = html_file.read()

        # Append stage name if not appended
        if not template_name.endswith('-' + stage):
            template_name = template_name + '-' + stage
        
        # Create mailjet template
        data = {
            "Author": "junction",
            "Name": template_name,
            "OwnerType": "apiKey",
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
                "Subject": template_name
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
    os.environ['STAGE'] = stage

    config_filename = stage + '.env'
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_filepath = os.path.join(parent_dir, config_filename)
    config = dotenv_values(config_filepath)

    template_subdir = 'services/templates'
    template_dir = os.path.join(parent_dir, template_subdir)

    templates = {}
    for file in os.listdir(template_dir):
        template_file_path = os.path.join(template_dir, file)
        template_name = "TempProject-" + os.path.splitext(os.path.basename(file))[0]
        mj_api_key = config['MJ_APIKEY_PUBLIC']
        mj_api_secret = config['MJ_APIKEY_PRIVATE']
        print(mj_api_key)
        print(mj_api_secret)
        print("Updating Mailjet template: " + template_name +
                " in stage: " + stage)
        template_id = create_or_update_mailjet_template(template_file_path, template_name, mj_api_key, mj_api_secret, stage)
        templates[template_name] = template_id

    print()
    print("==========================================================================")
    print("Templates created successfully on Mailjet. Following are the template IDs:")
    for name in templates:
        print(f'{name}: {templates[name]}')
    return True


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
