import boto
from boto.dynamodb2.table import Table, Item
from boto.dynamodb2.fields import GlobalAllIndex, HashKey, RangeKey

from teine import settings

conn = boto.dynamodb2.connect_to_region(
    settings.DYNAMO_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

table_prefix = '{}-'.format(settings.SCHEMA)


def init_test():
    global table_prefix
    table_prefix = '{}'.format(settings.SCHEMA_TEST)


def create_table(table_name, hash_key, range_key=None,
                 global_secondary_indexes=[]):
    default_throughput = {'read': 1, 'write': 1}

    def generate_index(idx):
        if len(idx) == 1:
            return GlobalAllIndex(
                _index_name(*idx),
                parts=[HashKey(idx[0])],
                throughput=default_throughput)
        if len(idx) == 2:
            return GlobalAllIndex(
                _index_name(*idx),
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


def query(table_name, hash_value, primary_hash_key=None, index_hash_key=None):
    table = Table(_table_name(table_name), connection=conn)
    cond = {
        'index': _index_name(index_hash_key) if index_hash_key else None,
        '{}__eq'.format(primary_hash_key or index_hash_key): hash_value
    }
    return table.query_2(**cond)


def scan(table_name, **kwargs):
    table = Table(_table_name(table_name), connection=conn)
    return table.scan(**kwargs)


def delete(table_name, **kwargs):
    table = Table(_table_name(table_name), connection=conn)
    table.delete_item(**kwargs)


def _table_name(name):
    return '{}{}'.format(table_prefix, name)


def _index_name(*args):
    result = 'index'
    for key in args:
        result = '{}-{}'.format(key, result)
    return result
