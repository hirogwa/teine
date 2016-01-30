import unittest
from unittest import mock
from teine import (personality_operations, models, externals,
                   operations_common, episode_operations)


class TestPersonalityOperations(unittest.TestCase):
    @classmethod
    def _twitter_user_generic(cls, screen_name='twitter_user_screen_name'):
        '''
        Returns twitter user data for generic purpose
        '''
        return {
            'screen_name': screen_name,
            'name': 'twitter user name',
            'description': 'twitter user description',
            'profile_image_url': 'twitter user image'
        }

    @classmethod
    def _personality_generic(cls, personality_id='p_id', episodes_as_host=[],
                             episodes_as_guest=[]):
        return models.Personality(
            personality_id, 'show_id', 'name', 'description',
            twitter=cls._twitter_user_generic(),
            episodes_as_host=episodes_as_host,
            episodes_as_guest=episodes_as_guest)

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

        twitter_user = self._twitter_user_generic(screen_name)
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

        twitter_user = self._twitter_user_generic(screen_name)
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

    @mock.patch.object(models.Personality, 'load')
    def test_add_host_to_episode_host_not_found(self, mock_personality_load):
        personality_id = 'p_id'
        episode_id = 'ep_id'
        mock_personality_load.return_value = None
        with self.assertRaises(ValueError):
            personality_operations.add_host_to_episode(
                personality_id, episode_id)
        mock_personality_load.assert_called_with(personality_id)

    @mock.patch.object(models.Personality, 'load')
    def test_add_host_to_episode_duplicate(self, mock_personality_load):
        episode_id = 'ep_id'
        p = self._personality_generic(episodes_as_host=[episode_id])
        p.save = mock.MagicMock(return_value=p)
        mock_personality_load.return_value = p

        personality_operations.add_host_to_episode(
            p.personality_id, episode_id)

        mock_personality_load.assert_called_with(p.personality_id)
        self.assertEqual(1, len(p.episodes_as_host))

    @mock.patch.object(models.Personality, 'load')
    def test_add_host_to_episode(self, mock_personality_load):
        episode_id = 'ep_id'
        p = self._personality_generic()
        p.save = mock.MagicMock(return_value=p)
        mock_personality_load.return_value = p

        personality_operations.add_host_to_episode(
            p.personality_id, episode_id)

        mock_personality_load.assert_called_with(p.personality_id)
        self.assertIn(episode_id, p.episodes_as_host)

    @mock.patch.object(models.Personality, 'load')
    def test_remove_host_from_episode_host_not_found(
            self, mock_personality_load):
        personality_id = 'p_id'
        episode_id = 'ep_id'
        mock_personality_load.return_value = None
        with self.assertRaises(ValueError):
            personality_operations.remove_host_from_episode(
                personality_id, episode_id)
        mock_personality_load.assert_called_with(personality_id)

    @mock.patch.object(models.Personality, 'load')
    def test_remove_host_from_episode(self, mock_personality_load):
        episode_id = 'ep_id'
        p = self._personality_generic(episodes_as_host=[episode_id])
        p.save = mock.MagicMock(return_value=p)
        mock_personality_load.return_value = p

        personality_operations.remove_host_from_episode(
            p.personality_id, episode_id)

        mock_personality_load.assert_called_with(p.personality_id)
        self.assertNotIn(episode_id, p.episodes_as_host)
        self.assertEqual(0, len(p.episodes_as_host))

    @mock.patch.object(models.Personality, 'load')
    def test_add_guest_to_episode_guest_not_found(self, mock_personality_load):
        personality_id = 'p_id'
        episode_id = 'ep_id'
        mock_personality_load.return_value = None

        with self.assertRaises(ValueError):
            personality_operations.add_guest_to_episode(
                personality_id, episode_id)
        mock_personality_load.assert_called_with(personality_id)

    @mock.patch.object(models.Personality, 'load')
    def test_add_guest_to_episode_duplicate(self, mock_personality_load):
        episode_id = 'ep_id'
        p = self._personality_generic(episodes_as_guest=[episode_id])
        p.save = mock.MagicMock(return_value=p)
        mock_personality_load.return_value = p

        personality_operations.add_guest_to_episode(
            p.personality_id, episode_id)

        mock_personality_load.assert_called_with(p.personality_id)
        self.assertEqual(1, len(p.episodes_as_guest))

    @mock.patch.object(models.Personality, 'load')
    def test_add_guest_to_episode(self, mock_personality_load):
        episode_id = 'ep_id'
        p = self._personality_generic()
        p.save = mock.MagicMock(return_value=p)
        mock_personality_load.return_value = p

        personality_operations.add_guest_to_episode(
            p.personality_id, episode_id)

        mock_personality_load.assert_called_with(p.personality_id)
        self.assertIn(episode_id, p.episodes_as_guest)

    @mock.patch.object(models.Personality, 'load')
    def test_remove_guest_from_episode_guest_not_found(
            self, mock_personality_load):
        personality_id = 'p_id'
        episode_id = 'ep_id'
        mock_personality_load.return_value = None

        with self.assertRaises(ValueError):
            personality_operations.remove_guest_from_episode(
                personality_id, episode_id)
        mock_personality_load.assert_called_with(personality_id)

    @mock.patch.object(models.Personality, 'load')
    def test_remove_guest_from_episode(self, mock_personality_load):
        episode_id = 'ep_id'
        p = self._personality_generic(episodes_as_guest=[episode_id])
        p.save = mock.MagicMock(return_value=p)
        mock_personality_load.return_value = p

        personality_operations.remove_guest_from_episode(
            p.personality_id, episode_id)

        mock_personality_load.assert_called_with(p.personality_id)
        self.assertNotIn(episode_id, p.episodes_as_guest)
        self.assertEqual(0, len(p.episodes_as_guest))

    @mock.patch.object(models.Personality, 'load')
    def test_delete_target_not_found(self, mock_personality_load):
        personality_id = 'p_id'
        mock_personality_load.return_value = None
        with self.assertRaises(ValueError):
            personality_operations.delete(personality_id)
        mock_personality_load.assert_called_with(personality_id)

    @mock.patch.object(episode_operations, 'remove_host')
    @mock.patch.object(episode_operations, 'remove_guest')
    @mock.patch.object(models.Personality, 'load')
    def test_delete(self, mock_personality_load,
                    mock_episode_remove_guest, mock_episode_remove_host):
        ep_id_as_host = 'ep_id_host'
        ep_id_as_guest = 'ep_id_guest'
        p = self._personality_generic(episodes_as_host=[ep_id_as_host],
                                      episodes_as_guest=[ep_id_as_guest])
        p.delete = mock.MagicMock(return_value=None)
        mock_personality_load.return_value = p

        personality_operations.delete(p.personality_id)

        mock_episode_remove_host.assert_called_with(
            ep_id_as_host, p.personality_id)
        mock_episode_remove_guest.assert_called_with(
            ep_id_as_guest, p.personality_id)
        p.delete.assert_called_with()

    @mock.patch.object(personality_operations, 'get_or_create')
    def test_people_to_ids(self, mock_get_or_create):
        show_id = 's_id'
        people_data = [{
            'source': 'twitter',
            'screen_name': 'testname01'
        }]
        p = self._personality_generic()
        mock_get_or_create.return_value = p

        result = personality_operations.people_to_ids(show_id, people_data)

        mock_get_or_create.assert_called_with(
            show_id,
            people_data[0].get('source'),
            people_data[0].get('screen_name'))
        self.assertEqual(result[0], p.personality_id)
