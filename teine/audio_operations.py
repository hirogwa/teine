import os

from teine import models, operations_common, s3_store


def get_by_user(user, include_used=True, include_unused=True):
    media_list = models.Media.load_all(user.user_id)
    if not include_used:
        media_list = list(filter(
            lambda x: x.episode_id is None, media_list))
    if not include_unused:
        media_list = list(filter(
            lambda x: x.episode_id is not None, media_list))
    return media_list


def create(user, uploaded_file):
    temp_f = operations_common.temp_filepath(uploaded_file.filename)
    uploaded_file.save(temp_f)
    media_info = {
        'content_type': uploaded_file.headers.get('Content-Type'),
        'size': os.stat(temp_f).st_size
    }
    media = models.Media.create(owner_user_id=user.user_id,
                                name=uploaded_file.filename,
                                **media_info)

    s3_store.set_key_public_read(media.media_id, temp_f)
    media.save()
    return media


def delete(media_id):
    media = models.Media.load(media_id)
    if media:
        media.delete()
        s3_store.delete_key(media_id)
    else:
        raise ValueError
