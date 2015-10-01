from teine import models, operations_common


def get_by_id(episode_id):
    return models.Episode.load(episode_id)


def get_by_show(show_id):
    return models.Episode.load_all(show_id)


def update(user, **kwargs):
    after = models.Episode(user.primary_show_id(), **_upd_params(**kwargs))
    before = models.Episode.load(after.episode_id)
    if not before:
        raise ValueError

    if before.media_id != after.media_id and before.media_id:
        _dissociate_media(before)

    if after.episode_id:
        _associate_media(after)

    return after.save()


def create(user, **kwargs):
    ep = models.Episode.create(user.primary_show_id(), **_upd_params())
    _associate_media(ep)
    return ep.save()


def delete(episode_id):
    ep = models.Episode.load(episode_id)
    if ep:
        if ep.media_id:
            _dissociate_media(ep)
        ep.delete()
    else:
        raise ValueError


def _associate_media(episode):
    if episode.media_id:
        media = models.Media.load(episode.media_id)
        media.episode_id = episode.episode_id
        media.save()
    return episode


def _dissociate_media(episode):
    media = models.Media.load(episode.media_id)
    media.episode_id = None
    media.save()
    episode.media_id = None
    return episode


def _upd_params(show_id, **kwargs):
    original = kwargs.copy()
    original.update({
        'guest_ids': operations_common.host_ids(show_id, kwargs.get('guests')),
        'links': map(lambda x: models.Link(**x), kwargs.get('links'))
    })
    return original
