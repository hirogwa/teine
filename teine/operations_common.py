import os

from teine import models, settings


def host_ids(show_id, people):
    '''
    Convert show hosts passed from the client to host ids,
    creating the host entites if necessary
    '''
    def find_personality_or_create(show_id, screen_name, name, description,
                                   profile_image_url, **kwargs):
        p = models.Personality.find_by_twitter(screen_name, show_id)
        if p:
            return p
        else:
            return models.Personality.create_from_twitter(
                show_id, screen_name, name, description, profile_image_url)

    return list(map(
        lambda x: find_personality_or_create(
            show_id, **x.get('twitter')).personality_id,
        people))


def temp_filepath(filename):
    if not os.path.exists(settings.TEMP_FILES_DIR):
        os.makedirs(settings.TEMP_FILES_DIR)
    return os.path.join(settings.TEMP_FILES_DIR, filename)
