import os
import unittest
from unittest.mock import MagicMock

from teine import models, s3_store, audio_operations, operations_common


class TestAudioOperations(unittest.TestCase):
    user = None
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.user = models.User(user_id='userId01',
                               password='hashedPass',
                               first_name='FirstName',
                               last_name='Awesome',
                               email='awesome@some.com')
        cls.predefined.append(
            models.Media(media_id='mediaId01',
                         owner_user_id=cls.user.user_id,
                         episode_id='episodeId01'))
        cls.predefined.append(
            models.Media(media_id='mediaId02',
                         owner_user_id=cls.user.user_id))

    @unittest.mock.patch.object(models.Media, 'load_all')
    def test_get_by_user(self, mock_media_load_all):
        mock_media_load_all.return_value = self.predefined
        expected = self.predefined
        actual = audio_operations.get_by_user(self.user)
        self.assertEqual(expected, actual)

    @unittest.mock.patch.object(models.Media, 'load_all')
    def test_get_by_user_filter_out_used(self, mock_media_load_all):
        mock_media_load_all.return_value = self.predefined
        expected = [self.predefined[1]]
        actual = audio_operations.get_by_user(self.user, include_used=False)
        self.assertEqual(expected, actual)

    @unittest.mock.patch.object(models.Media, 'load_all')
    def test_get_by_user_filter_out_unused(self, mock_media_load_all):
        mock_media_load_all.return_value = self.predefined
        expected = [self.predefined[0]]
        actual = audio_operations.get_by_user(self.user, include_unused=False)
        self.assertEqual(expected, actual)

    @unittest.mock.patch.object(models.Media, 'create')
    @unittest.mock.patch.object(s3_store, 'set_key_public_read')
    @unittest.mock.patch.object(os, 'stat')
    @unittest.mock.patch.object(operations_common, 'temp_filepath')
    def test_create(self, mock_filepath, mock_os_stat, mock_s3_set_key,
                    mock_media_create):
        expected = models.Media(media_id='someMediaId',
                                owner_user_id=self.user.user_id,
                                name='someFileName')

        uploaded_file = MagicMock()
        uploaded_file.filename = expected.name

        temp_filepath = 'tempFilePath'
        mock_filepath.return_value = temp_filepath

        os.stat = MagicMock()

        mock_media_create.return_value = expected
        expected.save = MagicMock()

        cr_actual = audio_operations.create(self.user, uploaded_file)

        self.assertEqual(expected, cr_actual)

        operations_common.temp_filepath.assert_called_with(
            uploaded_file.filename)
        s3_store.set_key_public_read.assert_called_with(
            expected.media_id, temp_filepath)
        expected.save.assert_called_with()

    @unittest.mock.patch.object(models.Media, 'load')
    def test_delete_non_existing_audio(self, mock_media_load):
        media_id = 'noSuchMeidaId'
        mock_media_load.return_value = None
        with self.assertRaises(ValueError):
            audio_operations.delete(media_id)
        models.Media.load.assert_called_with(media_id)

    @unittest.mock.patch.object(s3_store, 'delete_key')
    @unittest.mock.patch.object(models.Media, 'load')
    def test_delete(self, mock_media_load, mock_s3_delete_key):
        media = models.Media(media_id='someMediaId',
                             owner_user_id=self.user.user_id,
                             name='someFileName')
        mock_media_load.return_value = media
        media.delete = MagicMock()

        audio_operations.delete(media.media_id)
        media.delete.assert_called_with()
        s3_store.delete_key.assert_called_with(media.media_id)
