import os
import unittest
import uuid
from PIL import Image
from unittest import mock

from teine import s3_store, models, operations_common, photo_operations


class TestPhotoOperations(unittest.TestCase):
    user = None
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.user = models.User(user_id='userId01',
                               first_name='FirstName',
                               last_name='Awesome',
                               email='awesome@some.com')
        cls.predefined.append(models.Photo(photo_id='photoId01',
                                           owner_user_id=cls.user.user_id,
                                           thumbnail_id='thumbnailId01',
                                           filename='filename01'))
        cls.predefined.append(models.Photo(photo_id='photoId02',
                                           owner_user_id=cls.user.user_id,
                                           thumbnail_id='thumbnailId02',
                                           filename='filename02'))

    @mock.patch.object(models.Photo, 'load_all')
    def test_get_by_user(self, mock_photo_load_all):
        expected = list(filter(
            lambda x: x.owner_user_id == self.user.user_id, self.predefined))
        mock_photo_load_all.return_value = expected
        actual = photo_operations.get_by_user(self.user)
        self.assertEqual(expected, actual)
        models.Photo.load_all.assert_called_with(self.user.user_id)

    @mock.patch.object(models.Photo, 'create')
    @mock.patch.object(os, 'stat')
    @mock.patch.object(s3_store, 'set_key_public_read')
    @mock.patch.object(operations_common, 'temp_filepath')
    def test_create(self, mock_temp_filepath, mock_s3_set_key, mock_os,
                    mock_photo_create):
        photo = models.Photo(photo_id='photoId',
                             owner_user_id=self.user.user_id,
                             thumbnail_id='thumbnailId',
                             filename='fileName')
        thumbnail = '{}_thumbnail'.format(photo.filename)
        thumbnail_id = 'someNewThumbnailId'
        content_type = 'image/jpeg'
        image_type = 'jpeg'

        filepath_func = lambda x: '{}_mockPath'.format(x)
        mock_temp_filepath.side_effect = filepath_func
        uploaded_file = mock.MagicMock()
        uploaded_file.save = mock.MagicMock()
        uploaded_file.filename = photo.filename
        uploaded_file.headers = {'Content-Type': content_type}
        uuid.uuid4 = mock.MagicMock(return_value=thumbnail_id)
        im = mock.MagicMock()
        Image.open = mock.MagicMock(return_value=im)
        mock_photo_create.return_value = photo
        photo.save = mock.MagicMock()

        photo_operations.create(self.user, uploaded_file)

        operations_common.temp_filepath.assert_any_call(thumbnail)
        operations_common.temp_filepath.assert_any_call(photo.filename)
        uploaded_file.save.assert_called_with(filepath_func(photo.filename))
        uuid.uuid4.assert_called_with()
        Image.open.assert_called_with(filepath_func(photo.filename))
        im.thumbnail.assert_called_with((400, 400))
        im.save.assert_called_with(filepath_func(thumbnail), image_type)

        s3_store.set_key_public_read.assert_any_call(thumbnail_id,
                                                     filepath_func(thumbnail))
        s3_store.set_key_public_read.assert_any_call(
            photo.photo_id, filepath_func(photo.filename))
        photo.save.assert_called_with()

    @mock.patch.object(s3_store, 'delete_key')
    @mock.patch.object(models.Photo, 'load')
    def test_delete(self, mock_photo_load, mock_s3_delete_key):
        photo = models.Photo(photo_id='photoId',
                             owner_user_id=self.user.user_id,
                             thumbnail_id='thumbnailId',
                             filename='fileName')
        photo.delete = mock.MagicMock()
        mock_photo_load.return_value = photo
        photo_operations.delete(photo.photo_id)
        photo.delete.assert_called_with()
        s3_store.delete_key.assert_called_with(photo.photo_id)

    @mock.patch.object(models.Photo, 'load')
    def test_delete_non_existing_photo(self, mock_photo_load):
        photo_id = 'noSuchPhotoId'
        mock_photo_load.return_value = None
        with self.assertRaises(ValueError):
            photo_operations.delete(photo_id)
        models.Photo.load.assert_called_with(photo_id)
