import unittest
from unittest import mock

from teine import models, operations_common


class TestOperationsCommon(unittest.TestCase):
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.Personality(
            'personalityId01',
            'showId01',
            {'screen_name': 'hirogwa_test01',
             'name': 'Hiroki01',
             'description': 'only human 01',
             'profile_image_url': 'http://some.com/image_01.png'}))

        cls.predefined.append(models.Personality(
            'personalityId02',
            'showId01',
            {'screen_name': 'hirogwa_test02',
             'name': 'Name02',
             'description': 'only human 02',
             'profile_image_url': 'http://some.com/image_02.png'}))

    @mock.patch.object(models.Personality, 'find_by_twitter')
    def test_host_ids_existing(self, mock_find_by_twitter):
        show_id = 'showId01'
        expected = list(map(lambda x: x.personality_id, self.predefined))

        def mock_personality(screen_name, show_id):
            filtered = list(filter(
                lambda x:
                x.twitter_screen_name == screen_name and x.show_id == show_id,
                self.predefined))
            if len(filtered) == 1:
                return filtered[0]
            else:
                raise ValueError

        mock_find_by_twitter.side_effect = mock_personality
        people = list(map(lambda x: {'twitter': x.twitter}, self.predefined))

        actual = operations_common.host_ids(show_id, people)

        self.assertEqual(expected, actual)
        for i in range(len(self.predefined)):
            p = self.predefined[i]
            models.Personality.find_by_twitter.assert_any_call(
                p.twitter_screen_name, p.show_id)

    @mock.patch.object(models.Personality, 'create_from_twitter')
    @mock.patch.object(models.Personality, 'find_by_twitter')
    def test_host_ids_non_existing(self, mock_find_by_twitter,
                                   mock_create_from_twitter):
        show_id = 'showId01'
        people = list(map(lambda x: {'twitter': x.twitter}, self.predefined))
        expected = list(map(lambda x: x.personality_id, self.predefined))

        def mock_personality(show_id, screen_name, name, description,
                             profile_image_url):
            filtered = list(filter(
                lambda x:
                x.show_id == show_id and
                x.twitter_screen_name == screen_name and
                x.twitter.get('name') == name and
                x.twitter.get('description') == description and
                x.twitter.get('profile_image_url') == profile_image_url,
                self.predefined))
            if len(filtered) == 1:
                return filtered[0]
            else:
                raise ValueError

        mock_find_by_twitter.return_value = None
        mock_create_from_twitter.side_effect = mock_personality

        actual = operations_common.host_ids(show_id, people)

        self.assertEqual(expected, actual)

        for i in range(len(self.predefined)):
            p = self.predefined[i]
            models.Personality.find_by_twitter.assert_any_call(
                p.twitter.get('screen_name'), p.show_id)
            models.Personality.create_from_twitter.assert_any_call(
                p.show_id, p.twitter.get('screen_name'), p.twitter.get('name'),
                p.twitter.get('description'),
                p.twitter.get('profile_image_url'))
