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


def _describe_table(table):
    # NOTE: Table.describe() changes table.schema,
    # causing an error when querying a hash-only table
    return Table(table.table_name, connection=conn).describe().get('Table')


def query(table_name, partition_key, partition_value, sort_key=None,
          sort_value=None, sort_key_condition='eq'):
    '''
    :param sort_key_condition:
    '''
    table = Table(_table_name(table_name), connection=conn)
    cond = {
        '{}__eq'.format(partition_key): partition_value,
    }
    if sort_key:
        cond['{}__{}'.format(sort_key, sort_key_condition)] = sort_value

    table_description = _describe_table(table)
    attributes = [partition_key, sort_key] if sort_key else [partition_key]

    # query made against the primary partition key
    if _matches_primary_partition_key(table_description, attributes):
        return table.query_2(**cond)

    # query made against secondary indexes
    index = _find_matching_secondary_index(table_description, attributes)
    if index:
        cond['index'] = index
        return table.query_2(**cond)

    raise ValueError('Keys do not match those defined in the table. {}, {}'
                     .format(partition_key, sort_key))


def _matches_primary_partition_key(table_description, attributes):
    return attributes == list(map(
        lambda x: x.get('AttributeName'), table_description.get('KeySchema')))


def _find_matching_secondary_index(table_description, attributes):
    '''
    :param table_description: output of Table.describe()
    :param attributes: list of attributes to match for an index
    '''
    indexes = table_description.get('GlobalSecondaryIndexes')
    if not indexes:
        return None

    def _matches_index(param):
        key_schema = param.get('KeySchema')
        return attributes == list(map(
            lambda x: x.get('AttributeName'), key_schema))

    filtered = list(filter(lambda x: _matches_index(x), indexes))
    return filtered[0].get('IndexName') if len(filtered) > 0 else None


def scan(table_name, hash_value=None, primary_hash_key=None):
    table = Table(_table_name(table_name), connection=conn)
    cond = dict()
    if primary_hash_key:
        cond['{}__eq'.format(primary_hash_key)] = hash_value
    return table.scan(**cond)


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
