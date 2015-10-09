from unittest.mock import MagicMock
import unittest
import uuid

from teine import models, episode_operations, operations_common


class TestEpisodeOperation(unittest.TestCase):
    show_id_one = 'showId01'
    predefined = []
    user = models.User(user_id='userId',
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

    def test_get_by_id(self):
        expected = self.predefined[0]
        models.Episode.load = MagicMock(return_value=expected)

        actual = episode_operations.get_by_id(expected.episode_id)

        models.Episode.load.assert_called_with(expected.episode_id)
        self.assertEqual(expected, actual)

    def test_get_by_show(self):
        expected = [x for x in self.predefined
                    if x.show_id == self.show_id_one]
        models.Episode.load_all = MagicMock(return_value=expected)

        actual = episode_operations.get_by_show(self.show_id_one)

        models.Episode.load_all.assert_called_with(self.show_id_one)
        self.assertEqual(expected, actual)

    def test_update(self):
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
                               guest_ids=['someGuest', 'anotherGuest'],
                               links=[], status='someStatus')

        def media_load(media_id):
            if media_id == before.media_id:
                return media_before
            if media_id == after.media_id:
                return media_after
            raise ValueError

        models.Episode.load = MagicMock(return_value=before)
        models.Media.load = MagicMock(side_effect=media_load)
        media_before.save = MagicMock(return_value=media_before)
        operations_common.host_ids = MagicMock(return_value=after.guest_ids)
        media_after.save = MagicMock(return_value=media_after)
        before.save = MagicMock(return_value=before)

        actual = episode_operations.update(
            before.episode_id, after.title, after.summary, after.description,
            after.media_id, [], [], after.status)

        models.Episode.load.assert_called_with(before.episode_id)
        models.Media.load.assert_called_with(before.media_id)
        media_before.save.assert_called_with()
        operations_common.host_ids.assert_called_with(before.show_id, [])
        models.Media.load.assert_called_with(after.media_id)
        self.assertEqual(after.episode_id, actual.episode_id)
        self.assertEqual(after.show_id, actual.show_id)
        self.assertEqual(after.title, actual.title)
        self.assertEqual(after.summary, actual.summary)
        self.assertEqual(after.description, actual.description)
        self.assertEqual(after.guest_ids, actual.guest_ids)
        self.assertEqual(after.links, actual.links)
        self.assertEqual(after.status, actual.status)

    def test_update_non_existing_episode(self):
        episode_id = 'noSuchId'
        models.Episode.load = MagicMock(return_value=None)
        with self.assertRaises(ValueError):
            episode_operations.update(episode_id)
            models.Episode.load.assert_called_with(episode_id)

    def test_create_and_delete(self):
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
                                  guest_ids=['someGuest', 'anotherGuest'],
                                  links=[], status='someStatus')

        uuid.uuid4 = MagicMock(return_value=expected.episode_id)
        models.Episode.create = MagicMock(return_value=expected)
        operations_common.host_ids = MagicMock(return_value=expected.guest_ids)
        models.Media.load = MagicMock(return_value=media)
        media.save = MagicMock(return_value=media)
        expected.save = MagicMock(return_value=expected)

        actual = episode_operations.create(
            expected.show_id, expected.title, expected.summary,
            expected.description, expected.media_id, [], [], expected.status)

        models.Episode.create.assert_called_with(
            expected.episode_id, expected.show_id, expected.title,
            expected.summary, expected.description, expected.media_id,
            expected.guest_ids, expected.links, expected.status)
        operations_common.host_ids.assert_called_with(expected.show_id, [])
        models.Media.load.assert_called_with(expected.media_id)
        media.save.assert_called_with()
        expected.save.assert_called_with()
        self.assertEqual(expected, actual)

        # Delete
        media_id_before_dissociation = actual.media_id
        models.Episode.load = MagicMock(return_value=actual)
        models.Media.load = MagicMock(return_value=media)
        media.save = MagicMock(return_value=media)
        actual.delete = MagicMock(return_value=True)
        self.assertIsNone(episode_operations.delete(actual.episode_id))
        models.Episode.load.assert_called_with(actual.episode_id)
        models.Media.load.assert_called_with(media_id_before_dissociation)
        media.save.assert_called_with()
        actual.delete.assert_called_with()

    def test_delete_non_existing_episode(self):
        episode_id = 'noSuchId'
        models.Episode.load = MagicMock(return_value=None)
        with self.assertRaises(ValueError):
            episode_operations.delete(episode_id)
            models.Episode.load.assert_called_with(episode_id)
