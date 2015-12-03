import uuid

from teine import models, operations_common


def get_by_id(episode_id):
    return models.Episode.load(episode_id)


def get_by_show(show_id):
    return models.Episode.load_all(show_id)


def update(episode_id, title='', summary='', description='', media_id=None,
           guests=[], links=[], status=None, **kwargs):
    ep = models.Episode.load(episode_id)
    if not ep:
        raise ValueError

    if ep.media_id != media_id and ep.media_id:
        _dissociate_media(ep)

    params = _generated_params(ep.show_id, guests=guests, links=links)
    ep.title = title
    ep.summary = summary
    ep.description = description
    ep.media_id = media_id
    ep.guest_ids = params['guest_ids']
    ep.links = params['links']
    ep.status = status

    if ep.episode_id:
        _associate_media(ep)

    return ep.save()


def create(show_id, title='', summary='', description='', media_id=None,
           guests=[], links=[], status=None):
    params = _generated_params(show_id, guests=guests, links=links)
    ep = models.Episode.create(str(uuid.uuid4()), show_id, title, summary,
                               description, media_id,
                               params['guest_ids'], params['links'], status)
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


def _generated_params(show_id, guests=[], links=[]):
    return {
        'guest_ids': operations_common.host_ids(show_id, guests),
        'links': list(map(lambda x: models.Link(**x), links))
    }
