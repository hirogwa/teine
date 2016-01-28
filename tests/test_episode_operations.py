from unittest import mock
import unittest
import uuid

from teine import models, episode_operations, personality_operations


class TestEpisodeOperation(unittest.TestCase):
    show_id_one = 'showId01'
    predefined = []
    user = models.User(user_id='userId',
                       password='hashedPass',
                       first_name='FirstName',
                       last_name='LastName',
                       email='testuser@somedomain.com',
                       show_ids=['show01', 'show02'])

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(
            models.Episode(episode_id='episodeId01',
                           show_id=cls.show_id_one,
                           title='title01',
                           summary='summary01',
                           description='description01',
                           media_id='mediaId01'))
        cls.predefined.append(
            models.Episode(episode_id='episodeId02',
                           show_id=cls.show_id_one,
                           title='title02',
                           summary='summary02',
                           description='description02',
                           media_id='mediaId02'))

    @mock.patch.object(models.Episode, 'load')
    def test_get_by_id(self, mock_episode_load):
        expected = self.predefined[0]
        mock_episode_load.return_value = expected
        actual = episode_operations.get_by_id(expected.episode_id)

        models.Episode.load.assert_called_with(expected.episode_id)
        self.assertEqual(expected, actual)

    @mock.patch.object(models.Episode, 'load_all')
    def test_get_by_show(self, mock_episode_load_all):
        expected = [x for x in self.predefined
                    if x.show_id == self.show_id_one]
        mock_episode_load_all.return_value = expected

        actual = episode_operations.get_by_show(self.show_id_one)

        models.Episode.load_all.assert_called_with(self.show_id_one)
        self.assertEqual(expected, actual)

    @mock.patch.object(personality_operations, 'add_guest_to_episode')
    @mock.patch.object(personality_operations, 'add_host_to_episode')
    @mock.patch.object(personality_operations, 'people_to_ids')
    @mock.patch.object(models.Media, 'load')
    @mock.patch.object(models.Episode, 'load')
    def test_update(self, mock_episode_load, mock_media_load,
                    mock_people_to_ids, mock_add_host_to_episode,
                    mock_add_guest_to_episode):
        media_before = models.Media(
            media_id='mediaId01',
            owner_user_id=self.user.user_id,
            name='name01')
        media_after = models.Media(
            media_id='mediaId02',
            owner_user_id=self.user.user_id,
            name='name02')
        before = self.predefined[0]
        before.media_id = media_before.media_id
        after = models.Episode(episode_id=before.episode_id,
                               show_id=self.show_id_one,
                               title='title',
                               summary='summary',
                               description='description',
                               media_id=media_before.media_id,
                               host_ids=['someone', 'another'],
                               guest_ids=['someone', 'another'],
                               links=[], status='someStatus')

        def media_load(media_id):
            if media_id == before.media_id:
                return media_before
            if media_id == after.media_id:
                return media_after
            raise ValueError('Unexpected test input')

        mock_episode_load.return_value = before
        mock_media_load.side_effect = media_load
        media_before.save = mock.MagicMock(return_value=media_before)
        mock_people_to_ids.return_value = after.guest_ids
        media_after.save = mock.MagicMock(return_value=media_after)
        before.save = mock.MagicMock(return_value=before)

        people_data_host = []
        people_data_guest = []
        actual = episode_operations.update(
            before.episode_id, after.title, after.summary, after.description,
            after.media_id, people_data_host, people_data_guest, [],
            after.status)

        models.Episode.load.assert_called_with(before.episode_id)
        models.Media.load.assert_called_with(before.media_id)
        media_before.save.assert_called_with()
        mock_people_to_ids.assert_called_with(before.show_id,
                                              people_data_host)
        mock_people_to_ids.assert_called_with(before.show_id,
                                              people_data_guest)
        models.Media.load.assert_called_with(after.media_id)
        self.assertEqual(after.episode_id, actual.episode_id)
        self.assertEqual(after.show_id, actual.show_id)
        self.assertEqual(after.title, actual.title)
        self.assertEqual(after.summary, actual.summary)
        self.assertEqual(after.description, actual.description)
        self.assertEqual(after.host_ids, actual.host_ids)
        self.assertEqual(after.guest_ids, actual.guest_ids)
        self.assertEqual(after.links, actual.links)
        self.assertEqual(after.status, actual.status)

    @mock.patch.object(models.Episode, 'load')
    def test_update_non_existing_episode(self, mock_episode_load):
        episode_id = 'noSuchId'
        mock_episode_load.return_value = None
        with self.assertRaises(ValueError):
            episode_operations.update(episode_id)
            models.Episode.load.assert_called_with(episode_id)

    @mock.patch.object(personality_operations, 'people_to_ids')
    @mock.patch.object(models.Media, 'load')
    @mock.patch.object(models.Episode, 'load')
    @mock.patch.object(models.Episode, 'create')
    def test_create_and_delete(self, mock_episode_create, mock_episode_load,
                               mock_media_load, mock_people_to_ids):
        # Create
        media = models.Media(
            media_id='mediaId',
            owner_user_id=self.user.user_id,
            name='name')

        expected = models.Episode(episode_id='episodeId',
                                  show_id='showId',
                                  title='title',
                                  summary='summary',
                                  description='description',
                                  media_id=media.media_id,
                                  host_ids=['someone', 'another'],
                                  guest_ids=['someone', 'another'],
                                  links=[], status='someStatus')

        uuid.uuid4 = mock.MagicMock(return_value=expected.episode_id)
        mock_episode_create.return_value = expected
        mock_people_to_ids.return_value = expected.guest_ids
        mock_media_load.return_value = media
        media.save = mock.MagicMock(return_value=media)
        expected.save = mock.MagicMock(return_value=expected)

        people_data = []
        actual = episode_operations.create(
            expected.show_id, expected.title, expected.summary,
            expected.description, expected.media_id, people_data,
            people_data, status=expected.status)

        models.Episode.create.assert_called_with(
            expected.episode_id, expected.show_id, expected.title,
            expected.summary, expected.description, expected.media_id,
            status=expected.status)
        mock_people_to_ids.assert_called_with(expected.show_id, people_data)
        models.Media.load.assert_called_with(expected.media_id)
        media.save.assert_called_with()
        expected.save.assert_called_with()
        self.assertEqual(expected, actual)

        # Delete
        media_id_before_dissociation = actual.media_id
        mock_episode_load.return_value = actual
        mock_media_load.return_value = media
        media.save = mock.MagicMock(return_value=media)
        actual.delete = mock.MagicMock(return_value=True)
        self.assertIsNone(episode_operations.delete(actual.episode_id))
        models.Episode.load.assert_called_with(actual.episode_id)
        models.Media.load.assert_called_with(media_id_before_dissociation)
        media.save.assert_called_with()
        actual.delete.assert_called_with()

    @mock.patch.object(models.Episode, 'load')
    def test_delete_non_existing_episode(self, mock_episode_load):
        episode_id = 'noSuchId'
        mock_episode_load.return_value = None
        with self.assertRaises(ValueError):
            episode_operations.delete(episode_id)
            models.Episode.load.assert_called_with(episode_id)
