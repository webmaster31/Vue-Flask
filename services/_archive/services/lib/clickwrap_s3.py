import os
import boto3
import json
import logging

def should_dump_clickwrap():
    return os.getenv('CLICKWRAP_DUMPS_S3_BUCKET') and os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_ACCESS_KEY_SECRET')


def dump_clickwrap_to_s3(clickwrap_acceptance_data):
    if not should_dump_clickwrap():
        logging.warn('CLICKWRAP_DUMPS_S3_BUCKET, AWS_ACCESS_KEY_ID or AWS_ACCESS_KEY_SECRET env variable was not set. Not saving clickwrap dump.')
    else:
        logging.info("Uploading clickwrap acceptance data to S3.")
        s3_prefix = os.getenv('CLICKWRAP_DUMPS_S3_PREFIX', '')
        s3_key = f"{s3_prefix}{clickwrap_acceptance_data['user']['entity_id']}/{clickwrap_acceptance_data['clickwrap']['content_version']}.json"
        s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_ACCESS_KEY_SECRET'])
        response = s3.put_object(Bucket=os.environ['CLICKWRAP_DUMPS_S3_BUCKET'], Key=s3_key, Body=json.dumps(clickwrap_acceptance_data))
        return response
