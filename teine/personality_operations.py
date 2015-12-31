import uuid
from teine import models, externals, episode_operations, operations_common


def get_or_create(show_id, source, screen_name):
    '''
    Attempts to find an personality within the show
    by twitter screen name, and creates it if it does not exists
    '''
    if not source == models.Personality.SOURCE.twitter.name:
        raise ValueError('Unsupported source name:{}'.format(source))

    twitter_user = externals.twitter_user(screen_name)
    p = models.Personality.find_by_twitter(show_id, screen_name)
    if p:
        p.twitter['name'] = twitter_user.get('name')
        p.twitter['description'] = twitter_user.get('description')
        p.twitter['profile_image_url'] = twitter_user.get('profile_image_url')
        p.name = p.twitter.get('name')
        p.description = p.twitter.get('description')
    else:
        p = models.Personality.create_from_twitter(
            str(uuid.uuid4()), show_id, screen_name,
            twitter_user.get('name'), twitter_user.get('description'),
            twitter_user.get('profile_image_url'))

    _store_profile_image(p)
    p.save()
    return p


def add_host_to_episode(personality_id, episode_id):
    '''
    Adds the personality represented by the given id
    to the given episode as a host.

    The episode is NOT modified. It's the caller's responsibility
    to modify the episode's attribute accordingly
    '''
    personality = models.Personality.load(personality_id)
    if not personality:
        raise ValueError(
            'Personality not found with id:{}'.format(personality_id))

    if episode_id not in personality.episodes_as_host:
        personality.episodes_as_host.append(episode_id)
        personality.save()


def remove_host_from_episode(personality_id, episode_id):
    '''
    Removes the personality represented by the given id
    from the given episode as a host.

    The episode is NOT modified. It's the caller's responsibility
    to modify the episode's attribute accordingly
    '''
    personality = models.Personality.load(personality_id)
    if not personality:
        raise ValueError(
            'Personality not found with id:{}'.format(personality_id))

    if episode_id in personality.episodes_as_host:
        personality.episodes_as_host = [
            x for x in personality.episodes_as_host if x != episode_id]
        personality.save()


def add_guest_to_episode(personality_id, episode_id):
    '''
    Adds the personality represented by the given id
    to the given episode as a guest.

    The episode is NOT modified. It's the caller's responsibility
    to modify the episode's attribute accordingly
    '''
    personality = models.Personality.load(personality_id)
    if not personality:
        raise ValueError(
            'Personality not found with id:{}'.format(personality_id))

    if episode_id not in personality.episodes_as_guest:
        personality.episodes_as_guest.append(episode_id)
        personality.save()


def remove_guest_from_episode(personality_id, episode_id):
    '''
    Removes the personality represented by the given id
    from the given episode as a guest.

    The episode is NOT modified. It's the caller's responsibility
    to modify the episode's attribute accordingly
    '''
    personality = models.Personality.load(personality_id)
    if not personality:
        raise ValueError(
            'Personality not found with id:{}'.format(personality_id))

    if episode_id in personality.episodes_as_guest:
        personality.episodes_as_guest = [
            x for x in personality.episodes_as_guest if x != episode_id]


def delete(personality_id):
    '''
    Deletes the personality represented by the given id.

    Modifies and saves the status of the associated episodes for
    the personality's presence as a host/guest
    '''
    personality = models.Personality.load(personality_id)
    if not personality:
        raise ValueError(
            'Personality not found with id:{}'.format(personality_id))

    for episode_id in personality.episodes_as_guest:
        episode_operations.remove_guest(episode_id, personality.personality_id)
    for episode_id in personality.episodes_as_host:
        episode_operations.remove_host(episode_id, personality.personality_id)
    personality.delete()


def people_to_ids(show_id, people_data):
    '''
    Gets the personality ids for the given list of the people info.
    Creates new personality data if it does not exist.

    :param people_data: list of the people's info
    :type people_data: list of dict with attributes "source" and "screen_name"
    :returns: The list of the corresponding personality ids
    '''
    return map(lambda x: get_or_create(
        show_id, x.get('source'), x.get('screen_name')
    ).personality_id, people_data)


def _store_profile_image(personality):
    operations_common.store_resource_from_url(
        personality.twitter.get('profile_image_url'),
        'personality_profile_image',
        personality.personality_id
    )
    return personality
