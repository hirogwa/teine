from PIL import Image
import os
import uuid

import models
import operations_common
import s3_store


def get_by_user(user):
    return models.Photo.load_all(user.user_id)


def create(user, uploaded_file):
    temp_f = operations_common.temp_filepath(uploaded_file.filename)
    uploaded_file.save(temp_f)

    content_type = uploaded_file.headers.get('Content-Type')
    if content_type == 'image/jpeg':
        image_type = 'jpeg'
    if content_type == 'image/gif':
        image_type = 'gif'

    thumbnail = operations_common.temp_filepath(
        '{}_thumbnail'.format(uploaded_file.filename))
    thumbnail_id = str(uuid.uuid4())
    im = Image.open(temp_f)
    im.thumbnail((400, 400))
    im.save(thumbnail, image_type)
    s3_store.set_key_public_read(thumbnail_id, thumbnail)

    photo_info = {
        'content_type': uploaded_file.headers.get('Content-Type'),
        'size': os.stat(temp_f).st_size
    }
    photo = models.Photo.create(owner_user_id=user.user_id,
                                thumbnail_id=thumbnail_id,
                                filename=uploaded_file.filename,
                                **photo_info)

    s3_store.set_key_public_read(photo.photo_id, temp_f)
    return photo.save()


def delete(photo_id):
    photo = models.Photo.load(photo_id)
    if photo:
        photo.delete()
    else:
        raise ValueError
