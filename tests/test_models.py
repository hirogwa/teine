from unittest import mock
import unittest

from teine import models


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
            show_id='show01',
            twitter={
                'screen_name': 'some_test_screen_name',
                'name': 'some_test_name',
                'description': 'some_test_desc',
                'profile_image_url': 'some_test_url'
            }))

    @mock.patch('teine.dynamo.query')
    def test_load(self, mocked_query):
        personality = self.predefined[0]
        mocked_query.return_value = [personality.export()]
        result = models.Personality.load(personality.personality_id)
        self.assertEqual(personality, result)
        mocked_query.assert_called_with(
            personality.table_name, 'personality_id',
            personality.personality_id)

    @mock.patch('teine.dynamo.query')
    def test_find_by_twitter(self, mocked_query):
        personality = self.predefined[0]
        mocked_query.return_value = [personality.export()]
        result = models.Personality.find_by_twitter(
            personality.twitter_screen_name, personality.show_id)
        self.assertEqual(personality, result)
        mocked_query.assert_called_with(
            personality.table_name, 'show_id', personality.show_id,
            'twitter_screen_name', personality.twitter_screen_name)

    def test_create_from_twitter(self):
        personality = self.predefined[0]
        result = models.Personality.create_from_twitter(
            personality.personality_id, personality.show_id,
            **personality.twitter)
        self.assertEqual(personality, result)

    @mock.patch('teine.dynamo.update')
    def test_save(self, mocked_update):
        personality = self.predefined[0]
        result = personality.save()
        self.assertEqual(personality, result)
        mocked_update.assert_called_with(
            personality.table_name, personality.export())

    @mock.patch('teine.dynamo.delete')
    def test_delete(self, mocked_delete):
        personality = self.predefined[0]
        result = personality.delete()
        self.assertTrue(result)
        mocked_delete.assert_called_with(
            personality.table_name, personality_id=personality.personality_id)


class TestUser(unittest.TestCase):
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.User(
            user_id='user01',
            password='hashedPass01',
            first_name='firstName01',
            last_name='lastName01',
            email='email01',
            show_ids=['show01', 'show02']))
        cls.predefined.append(models.User(
            user_id='user02',
            password='hashedPass02',
            first_name='firstName02',
            last_name='lastName02',
            email='email02',
            show_ids=[]))

    @mock.patch('teine.dynamo.query')
    def test_load_by_id(self, mocked_query):
        user = self.predefined[0]

        # found
        mocked_query.return_value = [user.export(True)]
        result = models.User.load(user_id=user.user_id)
        self.assertEqual(user, result)

        # not found
        mocked_query.return_value = []
        result = models.User.load(user_id='no such id')
        self.assertEqual(None, result)

    @mock.patch('teine.dynamo.query')
    def test_load_by_email(self, mocked_query):
        user = self.predefined[0]

        # found
        mocked_query.return_value = [user.export(True)]
        result = models.User.load(email=user.email)
        self.assertEqual(user, result)

        # not found
        mocked_query.return_value = []
        result = models.User.load(email='no such email')
        self.assertEqual(None, result)

    def test_create(self):
        user = self.predefined[1]
        result = models.User.create(
            user.user_id, user.password, user.email, user.first_name,
            user.last_name)
        self.assertEqual(user, result)

    @mock.patch('teine.dynamo.update')
    def test_save(self, mocked_update):
        user = self.predefined[0]
        result = user.save()
        self.assertEqual(user, result)
        mocked_update.assert_called_with(user.table_name, user.export(True))

    @mock.patch('teine.dynamo.delete')
    def test_delete(self, mocked_delete):
        user = self.predefined[0]
        result = user.delete()
        self.assertTrue(result)
        mocked_delete.assert_called_with(user.table_name, user_id=user.user_id)
