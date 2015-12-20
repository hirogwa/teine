import time
import unittest

from teine import dynamo


class TestOthers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = {
            'primary_partition': {
                'table': 'test_table_01',
                'key': 'data_id',
                'indexes': []
            },
            'primary_partition_range': {
                'table': 'test_table_02',
                'key': 'data_id',
                'range': 'data_range',
                'indexes': []
            },
            'secondary_partition': {
                'table': 'test_table_11',
                'key': 'data_id',
                'indexes': [('index_key',)]
            },
            'secondary_partition_range': {
                'table': 'test_table_12',
                'key': 'data_id',
                'indexes': [('index_key', 'index_range')]
            }
        }

        # create test tables
        for key, t in cls.tables.items():
            print('Creating test table {}'.format(t['table']))
            dynamo.create_table(t['table'], t['key'], t.get('range'),
                                t.get('indexes'))
        print('Allowing 10 seconds for table creation...')
        time.sleep(10)

        # insert test data
        t_01 = cls.tables['primary_partition']
        dynamo.batch_write(t_01['table'], [{
            t_01['key']: 'id_01',
            'name': 'bonobono',
            'mind': 'slow'
        }, {
            t_01['key']: 'id_02',
            'name': 'shimarisu',
            'mind': 'dark'
        }, {
            t_01['key']: 'id_03',
            'name': 'araiguma',
            'mind': 'child'
        }])

        t_02 = cls.tables['primary_partition_range']
        dynamo.batch_write(t_02['table'], [{
            t_02['key']: 'walkable',
            t_02['range']: 'bonobono',
            'mind': 'slow'
        }, {
            t_02['key']: 'walkable',
            t_02['range']: 'shimarisu',
            'mind': 'dark'
        }, {
            t_02['key']: 'runnable',
            t_02['range']: 'araiguma',
            'mind': 'child'
        }])

        t_11 = cls.tables['secondary_partition']
        dynamo.batch_write(t_11['table'], [{
            t_11['key']: 'id_01',
            t_11['indexes'][0][0]: 'bonobono',
            'mind': 'slow'
        }, {
            t_11['key']: 'id_02',
            t_11['indexes'][0][0]: 'shimarisu',
            'mind': 'dark'
        }, {
            t_11['key']: 'id_03',
            t_11['indexes'][0][0]: 'araiguma',
            'mind': 'chiild'
        }])

        t_12 = cls.tables['secondary_partition_range']
        dynamo.batch_write(t_12['table'], [{
            t_12['key']: 'id_01',
            t_12['indexes'][0][0]: 'walkable',
            t_12['indexes'][0][1]: 'bonobono'
        }, {
            t_12['key']: 'id_02',
            t_12['indexes'][0][0]: 'walkable',
            t_12['indexes'][0][1]: 'shimarisu'
        }, {
            t_12['key']: 'id_03',
            t_12['indexes'][0][0]: 'runnable',
            t_12['indexes'][0][1]: 'araiguma'
        }])

    @classmethod
    def tearDownClass(cls):
        # drop the test tables
        print('')
        for key, t in cls.tables.items():
            table_name = t['table']
            print('Deleting {}'.format(table_name))
            dynamo.delete_table(table_name)

    def test_query_primary_partition_key(self):
        table = self.tables['primary_partition']
        result = dynamo.query(table['table'], 'id_01', table['key'])
        result = dynamo.query(table['table'], table['key'], 'id_01')
        val = result.next()
        self.assertEqual('id_01', val[table['key']])
        self.assertEqual('bonobono', val['name'])
        self.assertEqual('slow', val['mind'])

    def test_query_primary_sort_key_eq(self):
        table = self.tables['primary_partition_range']
        result = dynamo.query(table['table'], table['key'], 'walkable',
                              table['range'], 'bonobono')
        val = result.next()
        self.assertEqual('walkable', val[table['key']])
        self.assertEqual('bonobono', val[table['range']])
        self.assertEqual('slow', val['mind'])

    def test_query_secondary_partition_key(self):
        table = self.tables['secondary_partition']
        result = dynamo.query(table['table'],
                              table['indexes'][0][0], 'bonobono')
        val = result.next()
        self.assertEqual('id_01', val[table['key']])
        self.assertEqual('bonobono', val[table['indexes'][0][0]])
        self.assertEqual('slow', val['mind'])

    def test_query_secondary_sort_key_eq(self):
        table = self.tables['secondary_partition_range']
        result = dynamo.query(table['table'],
                              table['indexes'][0][0], 'walkable',
                              table['indexes'][0][1], 'bonobono')
        val = result.next()
        self.assertEqual('id_01', val[table['key']])
        self.assertEqual('walkable', val[table['indexes'][0][0]])
        self.assertEqual('bonobono', val[table['indexes'][0][1]])

    def test_no_matching_index(self):
        table = self.tables['primary_partition_range']
        with self.assertRaises(ValueError):
            dynamo.query(table['table'], table['range'], 'bonobono')
