import unittest
from unittest import mock
from teine import personality_operations, models, externals, operations_common


class TestPersonalityOperations(unittest.TestCase):
    def test_get_or_create_non_twitter(self):
        with self.assertRaises(ValueError):
            personality_operations.get_or_create(
                'showId', 'someNewSNS', 'someName')

    @mock.patch.object(operations_common, 'store_resource_from_url')
    @mock.patch.object(models.Personality, 'find_by_twitter')
    @mock.patch.object(externals, 'twitter_user')
    def test_get_or_create_existing_personality(
            self, mock_twitter_user, mock_find_by_twitter,
            mock_store_resource):
        show_id = 'showId'
        source = 'twitter'
        screen_name = 'testuser'

        twitter_user = {
            'screen_name': screen_name,
            'name': 'newName',
            'description': 'newDescription',
            'profile_image_url': 'newImage'
        }
        p = models.Personality(
            'id', 'showId', 'name', 'description', twitter={
                'screen_name': screen_name,
                'name': 'oldName',
                'description': 'oldDescription',
                'profile_image_url': 'oldImage'
            })

        mock_twitter_user.return_value = twitter_user
        mock_find_by_twitter.return_value = p
        p.save = mock.MagicMock(return_value=p)

        personality_operations.get_or_create(
            show_id, source, screen_name)

        mock_twitter_user.assert_called_with(screen_name)
        mock_find_by_twitter.assert_called_with(show_id, screen_name)
        mock_store_resource.assert_called_with(
            p.twitter.get('profile_image_url'),
            'personality_profile_image',
            p.personality_id)
        self.assertEqual(twitter_user.get('name'), p.name)
        self.assertEqual(twitter_user.get('description'), p.description)
        self.assertEqual(twitter_user, p.twitter)

    @mock.patch.object(operations_common, 'store_resource_from_url')
    @mock.patch.object(models.Personality, 'create_from_twitter')
    @mock.patch.object(models.Personality, 'find_by_twitter')
    @mock.patch.object(externals, 'twitter_user')
    def test_get_or_create_new_personality_from_twitter(
            self, mock_twitter_user, mock_find_by_twitter,
            mock_create_from_twitter, mock_store_resource):
        show_id = 'showId'
        source = 'twitter'
        screen_name = 'testuser'

        twitter_user = {
            'screen_name': screen_name,
            'name': 'newName',
            'description': 'newDescription',
            'profile_image_url': 'newImage'
        }
        p_expected = models.Personality(
            'id', show_id, twitter_user.get('name'),
            twitter_user.get('description'), twitter=twitter_user)

        mock_twitter_user.return_value = twitter_user
        mock_find_by_twitter.return_value = None
        mock_create_from_twitter.return_value = p_expected
        p_expected.save = mock.MagicMock(return_value=p_expected)

        p_created = personality_operations.get_or_create(
            show_id, source, screen_name)

        mock_twitter_user.assert_called_with(screen_name)
        mock_find_by_twitter.assert_called_with(show_id, screen_name)
        self.assertTrue(mock_create_from_twitter.called)
        mock_store_resource.assert_called_with(
            p_expected.twitter.get('profile_image_url'),
            'personality_profile_image',
            p_expected.personality_id)
        self.assertEqual(p_created, p_expected)

    def test_add_host_to_episode_host_not_found(self):
        self.assertTrue(False)

    def test_add_host_to_episode(self):
        self.assertTrue(False)

    def test_remove_host_from_episode_host_not_found(self):
        self.assertTrue(False)

    def test_remove_host_from_episode(self):
        self.assertTrue(False)

    def test_add_guest_to_episode_guest_not_found(self):
        self.assertTrue(False)

    def test_add_guest_to_episode(self):
        self.assertTrue(False)

    def test_remove_guest_from_episode_guest_not_found(self):
        self.assertTrue(False)

    def test_remove_guest_from_episode(self):
        self.assertTrue(False)

    def test_delete_target_not_found(self):
        self.assertTrue(False)

    def test_delete(self):
        self.assertTrue(False)

    def test_people_to_ids(self):
        self.assertTrue(False)
