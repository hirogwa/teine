import uuid
from teine import models, operations_common


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
        show.show_host_ids = operations_common.host_ids(show_id, show_hosts)
        show.image_id = image_id
        show.language = language
        return show.save()
    else:
        raise ValueError


def create(user, title='', author='', tagline='', description='',
           show_hosts=[], image_id='', language='en-us'):
    show_id = str(uuid.uuid4())
    return models.Show.create(show_id=show_id, owner_user_id=user.user_id,
                              title=title, author=author, tagline=tagline,
                              description=description,
                              show_host_ids=operations_common.host_ids(
                                  show_id, show_hosts),
                              image_id=image_id, language=language).save()
