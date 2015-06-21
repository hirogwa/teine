import datetime
import uuid

import dynamo
import settings


class Show():
    table_name = "teine-Show"

    def __init__(self, show_id, owner_user_id, title='', tagline='',
                 description='', show_host_ids=[], image_id='',
                 language='en-us', **kwargs):
        self.show_id = show_id
        self.owner_user_id = owner_user_id
        self.title = title
        self.tagline = tagline
        self.description = description
        self.show_host_ids = show_host_ids
        self.show_hosts = None
        self.image_id = image_id
        self.language = language

    @classmethod
    def create_new(cls, user_id, **kwargs):
        return Show(str(uuid.uuid4()), user_id, **kwargs)

    @classmethod
    def get_by_id(cls, show_id):
        rs = dynamo.query(cls.table_name, show_id__eq=show_id)
        for val in rs:
            return Show(**val)

        return None

    def load_hosts(self):
        if not self.show_hosts:
            self.show_hosts = map(
                lambda x: Personality.get_by_id(x), self.show_host_ids)
        return self

    def export(self):
        return {
            'show_id': self.show_id,
            'owner_user_id': self.owner_user_id,
            'title': self.title,
            'tagline': self.tagline,
            'description': self.description,
            'show_host_ids': self.show_host_ids,
            'show_hosts': list(map(
                lambda x: x.export(), self.show_hosts or [])),
            'image_id': self.image_id,
            'language': self.language
        }

    def save(self):
        dynamo.update(self.table_name, self.export())
        return self


class Episode():
    table_name = "teine-Episode"

    def __init__(self, episode_id, show_id,
                 title='', summary='', description='', media_id=None,
                 guest_ids=[], links=[], status=None, **kwargs):
        self.episode_id = episode_id
        self.show_id = show_id
        self.title = title
        self.summary = summary
        self.description = description
        self.media_id = media_id
        self._media = None
        self.guest_ids = guest_ids
        self._guests = []
        self.links = links
        self.status = status

    @classmethod
    def create_new(cls, show_id, **kwargs):
        return Episode(str(uuid.uuid4()), show_id, **kwargs)

    @classmethod
    def get_by_id(cls, episode_id):
        rs = dynamo.query(cls.table_name, episode_id__eq=episode_id)
        for val in rs:
            kwargs = val
            kwargs['links'] = map(lambda x: Link(**x), val.get('links') or [])
            return Episode(**kwargs)
        return None

    @classmethod
    def get_list(cls):
        rs = dynamo.scan(cls.table_name)

        def adjust(val):
            val['links'] = map(lambda x: Link(**x), val.get('links') or [])
            return Episode(**val)
        return [adjust(val) for val in rs]

    @property
    def guests(self):
        if not self._guests:
            self._guests = map(
                lambda x: Personality.get_by_id(x), self.guest_ids)
        return self._guests

    @property
    def media(self):
        if not self._media:
            self._media = (Media.get_by_id(self.media_id)
                           if self.media_id else None)
        return self._media

    def export(self):
        return {
            'episode_id': self.episode_id,
            'show_id': self.show_id,
            'title': self.title,
            'summary': self.summary,
            'description': self.description,
            'media_id': self.media_id,
            'media': self.media.export() if self.media else None,
            'guest_ids': self.guest_ids,
            'guests': list(map(lambda x: x.export(), self.guests)),
            'links': list(map(lambda x: x.export(), self.links)),
            'status': self.status
        }

    def save(self):
        dynamo.update(self.table_name, self.export())
        return self

    def delete(self):
        dynamo.delete(self.table_name, episode_id=self.episode_id)
        return True


class Link():
    def __init__(self, url, title):
        self.url = url
        self.title = title

    def export(self):
        return {
            'url': self.url,
            'title': self.title
        }


class Media():
    table_name = 'teine-Media'

    def __init__(self, media_id, owner_user_id, name='', content_type=None,
                 size=0, episode_id=None, datetime=None):
        self.media_id = media_id
        self.owner_user_id = owner_user_id
        self.name = name
        self.content_type = content_type
        self.size = size
        self.episode_id = episode_id
        self._episode = None
        self.datetime = datetime

    @classmethod
    def create_new(cls, owner_user_id, filename, **kwargs):
        return Media(
            str(uuid.uuid4()), owner_user_id, filename, **kwargs)

    @classmethod
    def get_by_id(cls, media_id):
        rs = dynamo.query(cls.table_name, media_id__eq=media_id)
        for val in rs:
            return Media(**val)
        return None

    @classmethod
    def get_list(cls, user_id):
        options = {
            'owner_user_id__eq': user_id
        }
        rs = dynamo.scan(cls.table_name, **options)
        return map(lambda x: Media(**x), rs)

    def associate_episode(self, episode_id):
        self.episode_id = episode_id
        return self

    def dissociate_episode(self):
        if not self.episode_id:
            raise ValueError('Media not associated with an episode ({}, {})'
                             .format(self.media_id, self.name))
        self.episode_id = None
        return self

    def associated_with_episode(self):
        return self.episode_id is not None

    @property
    def episode(self):
        if not self._episode:
            self._episode = Episode.get_by_id(self.episode_id)
        return self._episode

    def export(self):
        return {
            'media_id': self.media_id,
            'owner_user_id': self.owner_user_id,
            'episode_id': self.episode_id,
            'name': self.name,
            'content_type': self.content_type,
            'size': str(self.size),
            'datetime': self.datetime
        }

    def export_with_episode_summary(self):
        result = self.export()
        if self.episode_id:
            result['episode'] = {
                'episode_id': self.episode.episode_id,
                'title': self.episode.title,
                'status': self.episode.status
            }
        return result

    def save(self):
        data = self.export()
        data['datetime'] = datetime.datetime.utcnow().isoformat()
        dynamo.update(self.table_name, data)
        return self

    def delete(self):
        dynamo.delete(self.table_name, media_id=self.media_id)
        return self


class Personality():
    table_name = 'teine-Personality'

    def __init__(self, personality_id, show_id, twitter=None, **kwargs):
        self.personality_id = personality_id
        self.show_id = show_id
        self.twitter = twitter
        self.twitter_screen_name = (
            twitter.get('screen_name') if twitter else None)

    @classmethod
    def create_from_twitter(cls, screen_name, show_id,
                            name='', description='',
                            profile_image_url=None, **kwargs):
        return Personality(str(uuid.uuid4()), show_id, twitter={
            'screen_name': screen_name,
            'name': name,
            'description': description,
            'profile_image_url': profile_image_url
        })

    @classmethod
    def get_by_id(cls, personality_id):
        rs = dynamo.query(cls.table_name, personality_id__eq=personality_id)
        for val in rs:
            return Personality(**val)
        return None

    @classmethod
    def find_by_twitter(cls, screen_name, show_id=None,
                        create_when_not_found=False, **kwargs):
        index = {
            'index': 'twitter_screen_name-index',
            'twitter_screen_name__eq': screen_name
        }
        rs = dynamo.query(cls.table_name, **index)
        for val in rs:
            return Personality(**val)

        personality = Personality.create_from_twitter(
            screen_name, show_id, **kwargs)
        return personality.save() if create_when_not_found else personality

    def save(self):
        dynamo.update(self.table_name, self.export())
        return self

    def export(self):
        return {
            'personality_id': self.personality_id,
            'show_id': self.show_id,
            'twitter_screen_name': (
                self.twitter.get('screen_name') if self.twitter else None),
            'twitter': self.twitter
        }


class User():
    table_name = 'teine-User'

    def __init__(self, user_id, first_name='', last_name='', email='',
                 show_ids=[]):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.show_ids = show_ids

        self._is_authenticated = True
        self._is_active = True
        self._is_anonymous = False

    @classmethod
    def get_by_id(cls, user_id):
        rs = dynamo.query(cls.table_name, user_id__eq=user_id)
        for val in rs:
            return User(**val)
        return None

    @classmethod
    def get_by_credentials(cls, username, password):
        if (username == settings.TEST_USER_NAME and
                password == settings.TEST_USER_PASS):
            return User.get_by_id(settings.TEST_USER_ID)
        return None

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    def get_show_id(self):
        return self.show_ids[0] if len(self.show_ids) else None

    def export(self):
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'show_ids': self.show_ids
        }

    def save(self):
        dynamo.update(self.table_name, self.export())
        return self

    def is_authenticated(self):
        '''
        flask_login
        '''
        return self._is_authenticated

    def is_active(self):
        '''
        flask_login
        '''
        return self._is_active

    def is_anonymous(self):
        '''
        flask_login
        '''
        return self._is_anonymous

    def get_id(self):
        '''
        flask_login
        '''
        return self.user_id
