import json
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--no-open', '-n',
                        help='disables automatically opening the url in a browser',
                        action='store_true')
    args = parser.parse_args()
    no_open_flag = args.no_open

    return no_open_flag


def get_download_url():
    config_filename = 's3_config.json'
    method = 'get_object'

    with open(Path(__file__).parent / 'secrets' / config_filename) as config_file:
        s3_config_data = json.load(config_file)

    try:
        client = boto3.client('s3',
                              aws_access_key_id=s3_config_data['readonly_credentials']['aws_access_key_id'],
                              aws_secret_access_key=s3_config_data['readonly_credentials']['aws_secret_access_key'],
                              config=Config(region_name=s3_config_data['config']['region_name'],
                                            signature_version=s3_config_data['config']['signature_version'],
                                            retries={
                                                'max_attempts': s3_config_data['config']['retries']['max_attempts'],
                                                'mode': s3_config_data['config']['retries']['mode']}))
        return client.generate_presigned_url(ClientMethod=method,
                                             Params={'Bucket': s3_config_data['target']['bucket'],
                                                     'Key': s3_config_data['target']['key']},
                                             ExpiresIn=s3_config_data['parameters']['available_hours'] * 60 * 60)
    except ClientError:
        raise IOError(f'Have you filled out {config_filename}?')


def copy_to_clipboard(string):
    from sys import platform
    import subprocess

    os_lookup = {'win32': 'clip',
                 'darwin': 'pbcopy'}

    command = f'echo {string}|{os_lookup.get(platform, "")}'.replace('&', '^^^&')
    subprocess.check_call(command, shell=True)


def open_url(url):
    import webbrowser

    webbrowser.open(url)


if __name__ == '__main__':
    no_open_flag = parse_arguments()
    url = get_download_url()

    try:
        copy_to_clipboard(url)
        print('Download link (also copied to clipboard):')
    except:
        print('Download link:')
    print(url)

    if not no_open_flag:
        try:
            open_url(url)
        except:
            pass
