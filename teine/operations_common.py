import os

from teine import models, settings


def host_ids(show_id, people):
    '''
    Convert show hosts passed from the client to host ids,
    creating the host entites if necessary
    '''
    return list(map(
        lambda x: models.Personality.find_by_twitter(
            show_id=show_id,
            create_when_not_found=True,
            **x.get('twitter')).personality_id,
        people))


def temp_filepath(filename):
    if not os.path.exists(settings.TEMP_FILES_DIR):
        os.makedirs(settings.TEMP_FILES_DIR)
    return os.path.join(settings.TEMP_FILES_DIR, filename)
