import inspect
from teine import models, dynamo


def create_tables():
    for c in _classes_with_tables():
        print('Creating table for {}...'.format(c.__name__))
        dynamo.create_table(c.table_name, c.hash_key,
                            getattr(c, 'range_key', None),
                            getattr(c, 'secondary_indexes', []))


def delete_tables():
    for c in _classes_with_tables():
        print('Deleting table for {}...'.format(c.__name__))
        dynamo.delete_table(c.table_name)


def _classes_with_tables():
    return [cls for name, cls in inspect.getmembers(models)
            if inspect.isclass(cls) and hasattr(cls, 'table_name')]


if __name__ == '__main__':
    create_tables()
