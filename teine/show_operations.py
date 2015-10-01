from teine import models, operations_common


def get_by_id(user_id):
    return models.Show.load(user_id)


def update(user, show_hosts=[], **kwargs):
    if models.Show.load(kwargs.get('show_id')):
        return _create_instance_and_save(user, show_hosts, **kwargs)
    else:
        raise ValueError


def create(user, show_hosts=[], **kwargs):
    return _create_instance_and_save(user, show_hosts, **kwargs)


def _create_instance_and_save(user, show_hosts, **kwargs):
    return models.Show(
        owner_user_id=user.user_id,
        show_host_ids=operations_common.host_ids(
            user.primary_show_id(), show_hosts),
        **kwargs).save()
