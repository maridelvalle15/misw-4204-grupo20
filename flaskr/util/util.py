import os
import boto3
import botocore
from botocore.exceptions import NoCredentialsError

ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')

class util:

    def checkFileExists(file):
        client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        """return the key's size if it exist, else None"""
        response = client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=file,
        )
        for obj in response.get('Contents', []):
            if obj['Key'] == file:
                return True
        return False

    def uploadFileS3(inp_file_name, inp_file_key, content_type):
        client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        upload_file_response = client.put_object(Body=inp_file_name, Bucket=BUCKET_NAME, Key=inp_file_key, ContentType=content_type)
        print(f" ** Response - {upload_file_response}")

    def uploadFile(local_file_name, dest_file_name):
        client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        upload_file_response = client.upload_file(local_file_name, BUCKET_NAME, dest_file_name)
        print(f" ** Response - {upload_file_response}")

    def downloadFileS3(file_to_read):
        print(file_to_read)
        client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        fileobj = client.get_object(Bucket = BUCKET_NAME,Key = file_to_read)
        print(f" ** Response - {fileobj}")
        filedata = fileobj['Body'].read()

        return filedata

    def downloadFile(local_file_name,s3_file_name):
        client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name='us-east-1')
        download_file_response = client.download_file(BUCKET_NAME, s3_file_name, local_file_name)
        print(f" ** Response - {download_file_response}")

    def deleteFile(inp_file_name):
        client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        response = client.delete_object(Bucket=BUCKET_NAME, Key=inp_file_name)
        print(f" ** Response - {response}")
