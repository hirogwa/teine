from teine import models


def get_by_id(user_id):
    return models.User.load(user_id=user_id)


def get_by_credentials(username, password):
    return models.User.load(username=username, password=password)


def update(**kwargs):
    user_id = kwargs.get('user_id')
    if get_by_id(user_id):
        return models.User(**kwargs).save()
    else:
        raise ValueError
