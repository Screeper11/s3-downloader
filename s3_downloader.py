import json
import webbrowser
from pathlib import Path

import boto3
from botocore.config import Config

METHOD = 'get_object'


def get_download_link():
    with open(Path(__file__).parent / 's3_config.json') as config_file:
        s3_config_data = json.load(config_file)

    client = boto3.client('s3',
                          aws_access_key_id=s3_config_data['readonly_credentials']['aws_access_key_id'],
                          aws_secret_access_key=s3_config_data['readonly_credentials']['aws_secret_access_key'],
                          config=Config(region_name=s3_config_data['config']['region_name'],
                                        signature_version=s3_config_data['config']['signature_version'],
                                        retries={'max_attempts': s3_config_data['config']['retries']['max_attempts'],
                                                 'mode': s3_config_data['config']['retries']['mode']}))
    return client.generate_presigned_url(ClientMethod=METHOD,
                                         Params={'Bucket': s3_config_data['target']['bucket'],
                                                 'Key': s3_config_data['target']['key']},
                                         ExpiresIn=s3_config_data['parameters']['available_hours'] * 60 * 60)


if __name__ == '__main__':
    url = get_download_link()
    print(url)
    webbrowser.open(url)
