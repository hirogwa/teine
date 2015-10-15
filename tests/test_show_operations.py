from unittest import mock
import unittest
import uuid

from teine import dynamo, models, show_operations, operations_common


def setUpModule():
    dynamo.init_test()


class TestShowOperations(unittest.TestCase):
    predefined = []
    user = models.User(user_id='userId',
                       first_name='FirstName',
                       last_name='LastName',
                       email='testuser@somedomain.com',
                       show_ids=['show01', 'show02'])

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.Show(
            show_id='show01',
            owner_user_id='ownerUserId01',
            title='title01',
            author='author01',
            tagline='tagline01',
            description='description01',
            show_host_ids=['host01', 'host02'],
            image_id='image01',
            language='ja'))

    @mock.patch.object(models.Show, 'load')
    def test_get_by_id(self, mock_show_load):
        show_id = 'showId'
        show = models.Show(
            show_id=show_id,
            owner_user_id='ownerUserId',
            title='title',
            author='author',
            tagline='tagline',
            description='description',
            show_host_ids=['host01', 'host02'],
            image_id='image',
            language='ja')

        mock_show_load.return_value = show

        self.assertEqual(show, show_operations.get_by_id(show_id))
        models.Show.load.assert_called_with(show_id)

    @mock.patch.object(models.Show, 'create')
    @mock.patch.object(operations_common, 'host_ids')
    @mock.patch.object(uuid, 'uuid4')
    def test_create(self, mock_uuid, mock_host_ids, mock_show_create):
        args = {
            'show_id': 'newShowId',
            'owner_user_id': self.user.user_id,
            'title': 'newTitle',
            'author': 'newAuthor',
            'tagline': 'newTagline',
            'description': 'newDescription',
            'show_host_ids': ['showHost01', 'showHost02'],
            'image_id': 'newImage',
            'language': 'newLanguage'
        }
        expected = models.Show(**args)

        mock_uuid.return_value = args['show_id']
        mock_host_ids.return_value = args['show_host_ids']
        mock_show_create.return_value = expected
        expected.save = mock.MagicMock(return_value=expected)

        actual = show_operations.create(
            self.user, args['title'], args['author'], args['tagline'],
            args['description'], [], args['image_id'], args['language'])

        uuid.uuid4.assert_called_with()
        operations_common.host_ids.assert_called_with(args['show_id'], [])
        models.Show.create.assert_called_with(
            show_id=args['show_id'],
            owner_user_id=args['owner_user_id'],
            title=args['title'],
            author=args['author'],
            tagline=args['tagline'],
            description=args['description'],
            show_host_ids=args['show_host_ids'],
            image_id=args['image_id'],
            language=args['language'])
        expected.save.assert_called_with()

        self.assertEqual(expected.show_id, actual.show_id)
        self.assertEqual(expected.owner_user_id, actual.owner_user_id)
        self.assertEqual(expected.title, actual.title)
        self.assertEqual(expected.author, actual.author)
        self.assertEqual(expected.tagline, actual.tagline)
        self.assertEqual(expected.description, actual.description)
        self.assertEqual(expected.show_host_ids, actual.show_host_ids)
        self.assertEqual(expected.image_id, actual.image_id)
        self.assertEqual(expected.language, actual.language)

    @mock.patch.object(models.Show, 'load')
    @mock.patch.object(operations_common, 'host_ids')
    def test_update(self, mock_host_ids, mock_show_load):
        before = self.predefined[0]
        after_args = {
            'show_id': before.show_id,
            'owner_user_id': before.owner_user_id,
            'title': 'newTitle',
            'author': 'newAuthor',
            'tagline': 'newTagline',
            'description': 'newDescription',
            'show_host_ids': ['showHost01', 'showHost02'],
            'image_id': 'newImage',
            'language': 'newLanguage'
        }
        after = models.Show(**after_args)

        mock_host_ids.return_value = after_args['show_host_ids']
        mock_show_load.return_value = before
        before.save = mock.MagicMock(return_value=before)

        after_actual = show_operations.update(
            before.show_id, after_args['title'],
            after_args['author'], after_args['tagline'],
            after_args['description'], [], after_args['image_id'],
            after_args['language'])

        models.Show.load.assert_called_with(after_args['show_id'])
        operations_common.host_ids.assert_called_with(
            after_args['show_id'], [])
        before.save.assert_called_with()

        self.assertEqual(after.show_id, after_actual.show_id)
        self.assertEqual(after.owner_user_id, after_actual.owner_user_id)
        self.assertEqual(after.title, after_actual.title)
        self.assertEqual(after.author, after_actual.author)
        self.assertEqual(after.tagline, after_actual.tagline)
        self.assertEqual(after.description, after_actual.description)
        self.assertEqual(after.show_host_ids, after_actual.show_host_ids)
        self.assertEqual(after.image_id, after_actual.image_id)
        self.assertEqual(after.language, after_actual.language)

    @mock.patch.object(models.Show, 'load')
    def test_update_non_existing_show(self, mock_show_load):
        show_id = 'noSuchShow'
        mock_show_load.return_value = None

        with self.assertRaises(ValueError):
            show_operations.update(show_id)
            models.Show.load.assert_called_with(show_id)
