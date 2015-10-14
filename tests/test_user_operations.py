import unittest
from unittest import mock

from teine import models, user_operations


class TestUserOperations(unittest.TestCase):
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.User('userId01', 'FirstName', 'Awesome',
                                          'awesome@somedomain.com'))

    @mock.patch.object(models.User, 'load')
    def test_get_by_id(self, mock_user_load):
        mock_user_load.return_value = self.predefined[0]
        expected = self.predefined[0]
        actual = user_operations.get_by_id('userId01')
        self.assertEqual(expected, actual)

    @mock.patch.object(models.User, 'load')
    def test_update(self, mock_user_load):
        user = self.predefined[0]
        user.save = mock.MagicMock(return_value=user)
        new_first_name = 'newFirstName'
        new_last_name = 'stillAwesome'
        new_email = 'stillawesome@domain.com'
        new_show_ids = ['someShowId01']
        mock_user_load.return_value = user

        result = user_operations.update(
            user.user_id, new_first_name, new_last_name,
            new_email, new_show_ids)

        user.save.assert_called_with()
        self.assertEqual(result.user_id, user.user_id)
        self.assertEqual(result.first_name, new_first_name)
        self.assertEqual(result.last_name, new_last_name)
        self.assertEqual(result.email, new_email)
        self.assertEqual(result.show_ids, new_show_ids)

    @mock.patch.object(models.User, 'load')
    def test_update_non_existing_user(self, mock_user_load):
        user_id = 'noSuchUserId'
        mock_user_load.return_value = None
        with self.assertRaises(ValueError):
            user_operations.update(user_id, 'f_name', 'l_name', 'email', [])
        models.User.load.assert_called_with(user_id)