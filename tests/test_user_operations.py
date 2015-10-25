import unittest
from unittest import mock

from teine import models, user_operations


class TestUserOperations(unittest.TestCase):
    predefined = []

    @classmethod
    def setUpClass(cls):
        cls.predefined.append(models.User(
            'userId01', 'someHashedPass', 'awesome@somedomain.com',
            'FirstName', 'LastName'))

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

    @mock.patch.object(user_operations, 'get_by_email')
    @mock.patch.object(user_operations, 'get_by_id')
    @mock.patch.object(models.User, 'create')
    def test_signup(self, mock_user_create, mock_get_by_id, mock_get_by_email):
        mock_get_by_id.return_value = None
        mock_get_by_email.return_value = None
        user = models.User('userId', 'hashedPass', 'some@example.com',
                           'SomeFirstName', 'SomeLastName')
        user.save = mock.MagicMock(return_value=user)
        mock_user_create.return_value = user

        actual = user_operations.signup(user.user_id, user.password,
                                        user.email, user.first_name,
                                        user.last_name)

        self.assertEqual(user, actual)

        self.assertTrue(mock_user_create.called)
        user.save.assert_called_with()

    @mock.patch.object(user_operations, 'get_by_id')
    def test_signup_duplicate_user_id(self, mock_get_by_id):
        user = self.predefined[0]
        mock_get_by_id.return_value = user

        with self.assertRaises(user_operations.SignUpValidationException):
            user_operations.signup(user.user_id, 'pass01', 'some@email.com')
        mock_get_by_id.assert_called_with(user.user_id)

    @mock.patch.object(user_operations, 'get_by_id')
    @mock.patch.object(user_operations, 'get_by_email')
    def test_signup_duplicate_email(self, mock_get_by_email, mock_get_by_id):
        user = self.predefined[0]
        mock_get_by_id.return_value = None
        mock_get_by_email.return_value = user
        new_user_id = 'someUserId'

        with self.assertRaises(user_operations.SignUpValidationException):
            user_operations.signup(new_user_id, 'pass01', user.email)
        mock_get_by_id.assert_called_with(new_user_id)
        mock_get_by_email.assert_called_with(user.email)
