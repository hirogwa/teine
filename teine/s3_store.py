import boto
from teine import settings

conn = boto.s3.connect_to_region(
    settings.S3_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

bucket = conn.get_bucket(settings.S3_BUCKET_NAME)


def get_key(key_name, file_object):
    key = bucket.get_key(key_name)
    #key.get_file(file_object)
    return key.open()


def set_key_public_read(key_name, file_name):
    key = bucket.new_key(key_name)
    key.set_contents_from_filename(file_name)
    key.set_acl('public-read')


def delete_key(key_name):
    key = bucket.get_key(key_name)
    key.delete()
