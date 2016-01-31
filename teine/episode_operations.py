import uuid

from teine import models, personality_operations


def get_by_id(episode_id):
    return models.Episode.load(episode_id)


def get_by_show(show_id):
    return models.Episode.load_all(show_id)


def update(episode_id, title='', summary='', description='', media_id=None,
           hosts=[], guests=[], links=[], status=None, **kwargs):
    ep = models.Episode.load(episode_id)
    if not ep:
        raise ValueError

    if ep.media_id != media_id and ep.media_id:
        _dissociate_media(ep)

    ep.title = title
    ep.summary = summary
    ep.description = description
    ep.media_id = media_id
    ep.links = list(map(lambda x: models.Link(**x), links))
    ep.status = status
    _update_hosts(ep, hosts)
    _update_guests(ep, guests)
    _associate_media(ep)

    return ep.save()


def create(show_id, title='', summary='', description='', media_id=None,
           hosts=[], guests=[], links=[], status=None):
    ep = models.Episode.create(
        str(uuid.uuid4()), show_id, title, summary, description,
        media_id, status=status)
    ep.links = list(map(lambda x: models.Link(**x), links))
    _update_hosts(ep, hosts)
    _update_guests(ep, guests)
    _associate_media(ep)
    return ep.save()


def delete(episode_id):
    ep = models.Episode.load(episode_id)
    if ep:
        _update_hosts(ep, [])
        _update_guests(ep, [])
        if ep.media_id:
            _dissociate_media(ep)
        ep.delete()
    else:
        raise ValueError


def remove_host(episode_id, personality_id):
    '''
    Removes the personality from the episode's host list.
    This function does NOT modify the personality.
    '''
    episode = models.Episode.load(episode_id)
    if not episode:
        raise ValueError('No episode found with id:{}'.format(episode_id))

    if personality_id in episode.host_ids:
        episode.host_ids = [x for x in episode.host_ids if x != personality_id]
        episode.save()


def remove_guest(episode_id, personality_id):
    '''
    Removes the personality from the episode's guest list.
    This function does NOT modify the personality.
    '''
    episode = models.Episode.load(episode_id)
    if not episode:
        raise ValueError('No episode found with id:{}'.format(episode_id))

    if personality_id in episode.guest_ids:
        episode.guest_ids = [
            x for x in episode.guest_ids if x != personality_id]
        episode.save()


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


def _update_hosts(episode, host_data):
    host_ids = personality_operations.people_to_ids(episode.show_id, host_data)
    to_be_added = [x for x in host_ids if x not in episode.host_ids]
    to_be_removed = [x for x in episode.host_ids if x not in host_ids]

    for personality_id in to_be_added:
        personality_operations.add_host_to_episode(
            personality_id, episode.episode_id)
    for personality_id in to_be_removed:
        personality_operations.remove_host_from_episode(
            personality_id, episode.episode_id)

    episode.host_ids = host_ids
    return episode


def _update_guests(episode, guest_data):
    guest_ids = personality_operations.people_to_ids(
        episode.show_id, guest_data)
    to_be_added = [x for x in guest_ids if x not in episode.guest_ids]
    to_be_removed = [x for x in episode.guest_ids if x not in guest_ids]

    for personality_id in to_be_added:
        personality_operations.add_guest_to_episode(
            personality_id, episode.episode_id)
    for personality_id in to_be_removed:
        personality_operations.remove_guest_from_episode(
            personality_id, episode.episode_id)

    episode.guest_ids = guest_ids
    return episode
