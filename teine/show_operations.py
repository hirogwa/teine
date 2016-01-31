import uuid
from teine import models, personality_operations

DEFAULT_SHOW_TITLE = 'My first show'


def get_by_id(show_id):
    return models.Show.load(show_id)


def update(show_id, title='', author='', tagline='', description='',
           show_hosts=[], image_id='', language='en-us'):
    show = models.Show.load(show_id)
    if show:
        show.title = title
        show.author = author
        show.tagline = tagline
        show.description = description
        show.show_host_ids = personality_operations.people_to_ids(
            show_id, show_hosts)
        show.image_id = image_id
        show.language = language
        return show.save()
    else:
        raise ValueError


def create(user, title='', author='', tagline='', description='',
           show_hosts=[], image_id='', language='en-us'):
    show_id = str(uuid.uuid4())
    user.show_ids.append(show_id)
    user.save()
    show_host_ids = personality_operations.people_to_ids(show_id, show_hosts)
    return models.Show.create(show_id=show_id, owner_user_id=user.user_id,
                              title=title, author=author, tagline=tagline,
                              description=description,
                              show_host_ids=show_host_ids,
                              image_id=image_id, language=language).save()


def create_default(user):
    return create(user, title=DEFAULT_SHOW_TITLE, author=user.user_id)
