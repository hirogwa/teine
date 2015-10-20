import hashlib
from teine import models, settings


def get_by_id(user_id):
    return models.User.load(user_id=user_id)


def get_by_credentials(username, password):
    return models.User.load(username=username, password=_hash(password))


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


def signup(user_id, password, email, first_name, last_name):
    return models.User.create(
        user_id, _hash(password), email, first_name, last_name).save()


def _salt(s):
    return '{}{}'.format(settings.FIXED_SALT_STRING, s)


def _stretch(s):
    result = s
    for i in range(settings.STRETCH_COUNT):
        result = hashlib.sha256(result.encode(settings.ENCODING)).hexdigest()
    return result


def _hash(s):
    return _stretch(_salt(s))
