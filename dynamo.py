import settings
import boto
from boto.dynamodb2.table import Table
from boto.dynamodb2.table import Item

conn = boto.dynamodb2.connect_to_region(
    settings.DYNAMO_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


def update(table_name, data):
    table = Table(table_name, connection=conn)
    item = Item(table, data=data)
    return item.save(overwrite=True)


def batch_write(table_name, collection):
    table = Table(table_name, connection=conn)
    with table.batch_write() as batch:
        for item in collection:
            batch.put_item(data=item)


def get_item(table_name, **kwargs):
    table = Table(table_name, connection=conn)
    return table.get_item(**kwargs)


def query(table_name, **kwargs):
    table = Table(table_name, connection=conn)
    return table.query_2(**kwargs)


def scan(table_name, **kwargs):
    table = Table(table_name, connection=conn)
    return table.scan(**kwargs)


def delete(table_name, **kwargs):
    table = Table(table_name, connection=conn)
    table.delete_item(**kwargs)
