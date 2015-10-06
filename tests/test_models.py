import unittest

from teine import dynamo, models


def setUpModule():
    dynamo.init_test()


def tearDownModule():
    pass


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

        for x in cls.predefined:
            x.save()

    @classmethod
    def tearDownClass(cls):
        for x in cls.predefined:
            x.delete()

    def test_load(self):
        a = self.predefined[0]
        b = models.Show.load(a.show_id)
        self.assertEqual(a, b)

    def test_create_and_delete(self):
        a = models.Show.create(
            show_id='someShowId',
            owner_user_id='someUser',
            title='someTitle',
            author='someAuthor',
            tagline='someTagline',
            description='someDesc',
            show_host_ids=[],
            image_id='someImage',
            language='en-us')
        a.save()
        self.assertIsNotNone(models.Show.load(a.show_id))

        a.delete()
        self.assertIsNone(models.Show.load(a.show_id))


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
        for x in cls.predefined:
            x.save()

        cls.predefined_media = models.Media.create(
            owner_user_id='user01',
            name='name01')

        cls.predefined_media.save()

    @classmethod
    def tearDownClass(cls):
        for x in cls.predefined:
            x.delete()

        cls.predefined_media.delete()

    def test_load(self):
        a = self.predefined[0]
        b = models.Episode.load(a.episode_id)
        self.assertEqual(a, b)

    def test_create_and_delete(self):
        links = [models.Link(url='http://someurl01.com',
                             title='some link title 01'),
                 models.Link(url='http://someurl02.com',
                             title='some link title 02')]

        a = models.Episode.create(show_id='someShow',
                                  title='someTitle',
                                  summary='someSummary',
                                  description='someDescription',
                                  media_id=self.predefined_media.media_id,
                                  guest_ids=['someGuest', 'anotherGuest'],
                                  links=links,
                                  status='draft')
        a.save()
        self.assertIsNotNone(models.Episode.load(a.episode_id))

        a.delete()
        self.assertIsNone(models.Episode.load(a.episode_id))


class TestPhoto(unittest.TestCase):
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.Photo(
            photo_id='photo01',
            owner_user_id='user01',
            thumbnail_id='thumbnail01',
            filename='filename01'))

        for x in cls.predefined:
            x.save()

    @classmethod
    def tearDownClass(cls):
        for x in cls.predefined:
            x.delete()

    def test_laod(self):
        a = self.predefined[0]
        b = models.Photo.load(a.photo_id)
        self.assertEqual(a, b)

    def test_create_and_delete(self):
        a = models.Photo.create(
            owner_user_id='someUser',
            thumbnail_id='someThumbnail',
            filename='someFileName',
            size=3141592,
            content_type='image/jpeg')
        a.save()
        self.assertIsNotNone(models.Photo.load(a.photo_id))
        self.assertEqual(a, models.Photo.load(a.photo_id))

        a.delete()
        self.assertIsNone(models.Photo.load(a.photo_id))


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
        self.assertEqual(self.predefined[0], models.User.load(user_id='user'))
