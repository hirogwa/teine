import boto
from boto.dynamodb2.table import Table, Item
from boto.dynamodb2.fields import GlobalAllIndex, HashKey, RangeKey

from teine import settings

conn = boto.dynamodb2.connect_to_region(
    settings.DYNAMO_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

table_prefix = 'teine-'


def init_dev():
    global table_prefix
    table_prefix = 'teine-dev-'


def init_test():
    global table_prefix
    table_prefix = 'teine-test-'


def create_table(table_name, hash_key, range_key=None,
                 global_secondary_indexes=[]):
    default_throughput = {'read': 1, 'write': 1}

    def generate_index(idx):
        if len(idx) == 1:
            return GlobalAllIndex(
                '{}-index'.format(idx[0]),
                parts=[HashKey(idx[0])],
                throughput=default_throughput)
        if len(idx) == 2:
            return GlobalAllIndex(
                '{}-{}-index'.format(idx[0], idx[1]),
                parts=[HashKey(idx[0]), RangeKey(idx[1])],
                throughput=default_throughput)
        raise ValueError

    schema = [HashKey(hash_key)]
    if range_key:
        schema.append(RangeKey(range_key))

    table = Table.create(
        _table_name(table_name), schema=schema,
        throughput=default_throughput,
        global_indexes=list(map(
            lambda x: generate_index(x), global_secondary_indexes)),
        connection=conn)

    return table


def delete_table(table_name):
    table = Table(_table_name(table_name), connection=conn)
    table.delete()


def update(table_name, data):
    table = Table(_table_name(table_name), connection=conn)
    item = Item(table, data=data)
    return item.save(overwrite=True)


def batch_write(table_name, collection):
    table = Table(_table_name(table_name), connection=conn)
    with table.batch_write() as batch:
        for item in collection:
            batch.put_item(data=item)


def get_item(table_name, **kwargs):
    table = Table(_table_name(table_name), connection=conn)
    return table.get_item(**kwargs)


def query(table_name, **kwargs):
    table = Table(_table_name(table_name), connection=conn)
    return table.query_2(**kwargs)


def scan(table_name, **kwargs):
    table = Table(_table_name(table_name), connection=conn)
    return table.scan(**kwargs)


def delete(table_name, **kwargs):
    table = Table(_table_name(table_name), connection=conn)
    table.delete_item(**kwargs)


def _table_name(name):
    return '{}{}'.format(table_prefix, name)
