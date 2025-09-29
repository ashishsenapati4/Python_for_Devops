#!/usr/bin/env python

import boto3

#Get s3 client
s3 = boto3.client('s3')

#Define the bucket name and file to upload
bucket_name = 'botopython8899'
file_name = input("Enter file name you want to upload:")
object_name = file_name

#Upload the file to s3
try:
    s3.upload_file(file_name,bucket_name,object_name)
    print(f"file {file_name} uploaded to bucket {bucket_name} as {object_name}")

except Exception as e:
    print(f"Error uploading file: {e}")
