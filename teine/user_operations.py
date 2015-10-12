from teine import models


def get_by_id(user_id):
    return models.User.load(user_id=user_id)


def get_by_credentials(username, password):
    '''
    TODO test only
    '''
    return models.User.load(username=username, password=password)


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
