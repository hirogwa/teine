import hashlib
import re
from teine import models, settings, show_operations


class SignUpValidationException(Exception):
    def __init__(self, message):
        self.message = message


def get_by_id(user_id):
    return models.User.load(user_id=user_id)


def get_by_email(email):
    return models.User.load(email=email)


def get_by_credentials(user_id, password):
    user = models.User.load(user_id=user_id)
    return user if user and user.password == _hash(password) else None


def update(user_id, first_name, last_name, email, show_ids):
    user = models.User.load(user_id)
    if user:
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.show_ids = show_ids
        return user.save()
    else:
        raise ValueError


def signup(user_id, password, email, first_name='', last_name=''):
    validateSignupEntryOrRaise(user_id, password, email)
    user = models.User.create(
        user_id, _hash(password), email, first_name, last_name).save()
    show_operations.create_default(user)
    return user


def validateSignupEntryOrRaise(user_id, password, email):
    _validateInputOrRaise(user_id, password, email)
    _checkDuplicateOrRaise(user_id, email)


def _validateInputOrRaise(user_id, password, email):
    if len(user_id) < 1:
        raise SignUpValidationException('user_id empty')
    if not re.match('[^@]+@[^@]+\.[^@]', email):
        raise SignUpValidationException('invalid email format')
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        raise SignUpValidationException('password too short')


def _checkDuplicateOrRaise(user_id, email):
    if get_by_id(user_id):
        raise SignUpValidationException(
            'user_id already exists: {}'.format(user_id))
    if get_by_email(email):
        raise SignUpValidationException(
            'email already registered: {}'.format(email))


def _salt(s):
    return '{}{}'.format(settings.FIXED_SALT_STRING, s)


def _stretch(s):
    result = s
    for i in range(settings.STRETCH_COUNT):
        result = hashlib.sha256(result.encode(settings.ENCODING)).hexdigest()
    return result


def _hash(s):
    return _stretch(_salt(s))
