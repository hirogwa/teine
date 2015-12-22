from unittest import mock
import inspect
import time
import unittest

from teine import dynamo, models


def setUpModule():
    dynamo.init_test()
    for c in _classes_with_tables():
        print('Creating table for {}...'.format(c.__name__))
        dynamo.create_table(c.table_name, c.hash_key,
                            getattr(c, 'range_key', None),
                            getattr(c, 'secondary_indexes', []))

    print('Allowing 10 seconds for table creation...')
    time.sleep(10)


def tearDownModule():
    for c in _classes_with_tables():
        print('Deleting table for {}...'.format(c.__name__))
        dynamo.delete_table(c.table_name)


def _classes_with_tables():
    return [cls for name, cls in inspect.getmembers(models)
            if inspect.isclass(cls) and hasattr(cls, 'table_name')]


class TestShow(unittest.TestCase):
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.Show(
            show_id='showId01',
            owner_user_id='ownerUserId01',
            title='title01',
            author='author01',
            tagline='tagline01',
            description='description01',
            show_host_ids=['host01', 'host02'],
            image_id='image01',
            language='ja'))

    @mock.patch('teine.dynamo.query')
    def test_load(self, mocked_query):
        expected = self.predefined[0]
        mocked_query.return_value = [{
            'show_id': expected.show_id,
            'owner_user_id': expected.owner_user_id,
            'title': expected.title,
            'author': expected.author,
            'tagline': expected.tagline,
            'description': expected.description,
            'show_host_ids': expected.show_host_ids,
            'image_id': expected.image_id,
            'language': expected.language
        }]
        actual = models.Show.load(expected.show_id)
        mocked_query.assert_called_with(
            models.Show.table_name, 'show_id', expected.show_id)
        self.assertEqual(expected, actual)

    def test_create(self):
        show = self.predefined[0]
        result = models.Show.create(
            show.show_id, show.owner_user_id, show.title, show.author,
            show.tagline, show.description, show.show_host_ids, show.image_id,
            show.language)
        self.assertEqual(show, result)

    @mock.patch('teine.dynamo.update')
    def test_save(self, mocked_update):
        show = self.predefined[0]
        result = show.save()
        mocked_update.assert_called_with(show.table_name, show.export())
        self.assertEqual(show, result)

    @mock.patch('teine.dynamo.delete')
    def test_delete(self, mocked_delete):
        show = self.predefined[0]
        result = show.delete()
        mocked_delete.assert_called_with(show.table_name, show_id=show.show_id)
        self.assertTrue(result)


class TestEpisode(unittest.TestCase):
    predefined = []
    predefined_media = None

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.Episode(
            episode_id='episode01',
            show_id='show01',
            title='title01',
            summary='summary01',
            description='description01'))
        cls.predefined.append(models.Episode(
            episode_id='episode02',
            show_id='show01',
            title='title02',
            summary='summary02',
            description='description02'))
        cls.predefined.append(models.Episode(
            episode_id='episode03',
            show_id='show02',
            title='title03',
            summary='summary03',
            description='description03'))

        cls.predefined_media = models.Media.create(
            owner_user_id='user01',
            name='name01')

    @mock.patch('teine.dynamo.query')
    def test_load(self, mocked_query):
        episode = self.predefined[0]
        mocked_query.return_value = [{
            'episode_id': episode.episode_id,
            'show_id': episode.show_id,
            'title': episode.title,
            'summary': episode.summary,
            'description': episode.description
        }]
        result = models.Episode.load(episode.episode_id)
        self.assertEqual(episode, result)
        mocked_query.assert_called_with(
            episode.table_name, 'episode_id', episode.episode_id)

    @mock.patch('teine.dynamo.scan')
    def test_load_all(self, mocked_scan):
        episodes = self.predefined[:2]
        mocked_scan.return_value = [{
            'episode_id': episodes[0].episode_id,
            'show_id': episodes[0].show_id,
            'title': episodes[0].title,
            'summary': episodes[0].summary,
            'description': episodes[0].description
        }, {
            'episode_id': episodes[1].episode_id,
            'show_id': episodes[1].show_id,
            'title': episodes[1].title,
            'summary': episodes[1].summary,
            'description': episodes[1].description
        }]
        result = models.Episode.load_all(episodes[0].show_id)
        self.assertEqual(episodes, result)
        mocked_scan.assert_called_with(
            episodes[0].table_name, episodes[0].show_id, 'show_id')

    def test_create(self):
        episode = self.predefined[0]
        result = models.Episode.create(
            episode.episode_id, episode.show_id, episode.title,
            episode.summary, episode.description, episode.media_id,
            episode.guest_ids, episode.links, episode.status)
        self.assertEqual(episode, result)

    @mock.patch('teine.dynamo.update')
    def test_save(self, mocked_update):
        episode = self.predefined[0]
        result = episode.save()
        self.assertEqual(episode, result)
        mocked_update.assert_called_with(
            episode.table_name, episode.export(expand=['media', 'links']))

    @mock.patch('teine.dynamo.delete')
    def test_delete(self, mocked_delete):
        episode = self.predefined[0]
        result = episode.delete()
        self.assertTrue(result)
        mocked_delete.assert_called_with(
            episode.table_name, episode_id=episode.episode_id)


class TestPhoto(unittest.TestCase):
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.Photo(
            photo_id='photo01',
            owner_user_id='user01',
            thumbnail_id='thumbnail01',
            filename='filename01'))
        cls.predefined.append(models.Photo(
            photo_id='photo02',
            owner_user_id='user01',
            thumbnail_id='thumbnail02',
            filename='filename02'))
        cls.predefined.append(models.Photo(
            photo_id='photo03',
            owner_user_id='user02',
            thumbnail_id='thumbnail03',
            filename='filename03'))

    @mock.patch('teine.dynamo.query')
    def test_load(self, mocked_query):
        photo = self.predefined[0]
        mocked_query.return_value = [{
            'photo_id': photo.photo_id,
            'owner_user_id': photo.owner_user_id,
            'thumbnail_id': photo.thumbnail_id,
            'filename': photo.filename
        }]
        result = models.Photo.load(photo.photo_id)
        self.assertEqual(photo, result)
        mocked_query.assert_called_with(
            photo.table_name, 'photo_id', photo.photo_id)

    @mock.patch('teine.dynamo.scan')
    def test_load_all(self, mocked_scan):
        photos = self.predefined[:2]
        mocked_scan.return_value = [{
            'photo_id': photos[0].photo_id,
            'owner_user_id': photos[0].owner_user_id,
            'thumbnail_id': photos[0].thumbnail_id,
            'filename': photos[0].filename
        }, {
            'photo_id': photos[1].photo_id,
            'owner_user_id': photos[1].owner_user_id,
            'thumbnail_id': photos[1].thumbnail_id,
            'filename': photos[1].filename
        }]
        result = models.Photo.load_all(photos[0].owner_user_id)
        self.assertEqual(photos, list(result))
        mocked_scan.assert_called_with(
            photos[0].table_name, photos[0].owner_user_id, 'owner_user_id')

    def test_create(self):
        photo = self.predefined[0]
        result = models.Photo.create(
            photo_id=photo.photo_id, owner_user_id=photo.owner_user_id,
            thumbnail_id=photo.thumbnail_id, filename=photo.filename)
        self.assertEqual(photo, result)

    @mock.patch('teine.dynamo.update')
    def test_save(self, mocked_update):
        photo = self.predefined[0]
        result = photo.save()
        self.assertEqual(photo, result)
        mocked_update.assert_called_with(photo.table_name, photo.export())

    @mock.patch('teine.dynamo.delete')
    def test_delete(self, mocked_delete):
        photo = self.predefined[0]
        result = photo.delete()
        self.assertTrue(result)
        mocked_delete.assert_called_with(
            photo.table_name, photo_id=photo.photo_id)


class TestPersonality(unittest.TestCase):
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.Personality(
            personality_id='personality01',
            show_id='show01'))

        for x in cls.predefined:
            x.save()

    @classmethod
    def tearDownClass(cls):
        for x in cls.predefined:
            x.delete()

    def test_load(self):
        a = self.predefined[0]
        b = models.Personality.load(a.personality_id)
        self.assertEqual(a, b)

    def test_create_from_and_find_by_twitter(self):
        screen_name = 'testHirogwa'
        show_id = 'someShow'

        a = models.Personality.create_from_twitter(
            screen_name=screen_name,
            show_id=show_id,
            name='Mr. Random',
            description='some random guy',
            profile_image_url='https://some.url.com/someImage.png')
        a.save()
        self.assertEqual(a, models.Personality.find_by_twitter(
            screen_name, show_id))

        a.delete()
        self.assertIsNone(models.Personality.find_by_twitter(
            screen_name, show_id))


class TestUser(unittest.TestCase):
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.User(
            user_id='user',
            password='hashedPass',
            first_name='firstName',
            last_name='lastName',
            email='email',
            show_ids=['show01', 'show02']))

        for x in cls.predefined:
            x.save()

    @classmethod
    def tearDownClass(cls):
        for x in cls.predefined:
            x.delete()

    def test_load_by_id(self):
        user = self.predefined[0]
        self.assertEqual(user, models.User.load(user_id=user.user_id))
        self.assertEqual(None, models.User.load(user_id='noSuchUserId'))

    def test_load_by_email(self):
        user = self.predefined[0]
        self.assertEqual(user, models.User.load(email=user.email))
        self.assertEqual(None, models.User.load(email='noSuch@example.com'))

    def test_create_and_delete(self):
        user_id = 'userId'
        user = models.User.create(user_id, 'hashedPass', 'example@email.com',
                                  'FirstName', 'LastName')
        user.save()
        self.assertIsNotNone(models.User.load(user_id=user_id))

        user.delete()
        self.assertIsNone(models.User.load(user_id=user_id))
