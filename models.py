import dynamo
import uuid

import settings


class Show():
    table_name = "teine-Show"

    def __init__(self, show_id, user, title='', tagline='',
                 description='', show_hosts=[], episodes=[]):
        self.show_id = show_id
        self.owner_user = user
        self.title = title
        self.tagline = tagline
        self.description = description
        self.show_hosts = show_hosts
        self.episodes = episodes

    @classmethod
    def create_new(cls, user, **kwargs):
        return Show(str(uuid.uuid4()), user,
                    title=kwargs.get('title'),
                    tagline=kwargs.get('tagline'),
                    description=kwargs.get('description'),
                    show_hosts=map(
                        lambda x: Personality.create_new(**x),
                        kwargs.get('show_hosts')))

    @classmethod
    def get_by_id(cls, show_id, user):
        rs = dynamo.query(cls.table_name, show_id__eq=show_id)
        for val in rs:
            return Show(show_id, user,
                        title=val.get('title'),
                        tagline=val.get('tagline'),
                        description=val.get('description'),
                        show_hosts=map(
                            lambda x: Personality(**x),
                            val.get('show_hosts') or []),
                        episodes=map(
                            lambda ep_id: Episode(ep_id),
                            val.get('episodes') or []))

        return None

    def export(self):
        return {
            'show_id': self.show_id,
            'owner_user': self.owner_user.user_id,
            'title': self.title,
            'tagline': self.tagline,
            'description': self.description,
            'show_hosts': list(
                map(lambda x: x.export(), self.show_hosts)),
            'episodes': list(map(lambda x: x.episode_id, self.episodes))
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
        self.media = None
        self.guest_ids = guest_ids
        self.guests = []
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

    def load_guests(self):
        self.guests = map(lambda x: Personality.get_by_id(x), self.guest_ids)
        return self

    def load_media(self):
        self.media = Media.get_by_id(self.media_id) if self.media_id else None
        return self

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

    def __init__(self, media_id, owner_user, name='', content_type=None,
                 size=0, episode_id=None, status=None, schedule_date=None):
        self.media_id = media_id
        self.owner_user = owner_user
        self.name = name
        self.content_type = content_type
        self.size = size
        self.episode_id = episode_id
        self.status = status
        self.schedule_date = schedule_date

    @classmethod
    def create_new(cls, owner_user_id, filename, **kwargs):
        return Media(
            str(uuid.uuid4()), owner_user_id, filename,
            status='draft', **kwargs)

    @classmethod
    def get_by_id(cls, media_id):
        rs = dynamo.query(cls.table_name, media_id__eq=media_id)
        for val in rs:
            return Media(**val)
        return None

    @classmethod
    def get_list(cls, user):
        rs = dynamo.scan(cls.table_name)
        return map(lambda x: Media(**x), rs)

    def associate_episode(self, episode_id, status, schedule_date=None):
        self.episode_id = episode_id
        self.status = status
        self.schedule_date = schedule_date
        return self

    def dissociate_episode(self):
        self.episode_id = None
        return self

    def associated_with_episode(self):
        return self.episode_id is not None

    def export(self):
        return {
            'media_id': self.media_id,
            'owner_user': self.owner_user,
            'episode_id': self.episode_id,
            'name': self.name,
            'content_type': self.content_type,
            'size': str(self.size),
            'status': self.status,
            'schedule_date': self.schedule_date
        }

    def save(self):
        dynamo.update(self.table_name, self.export())
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

    def __init__(self, user_id=None, shows=[]):
        self.user_id = user_id
        self.shows = shows

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
        return self.shows[0] if len(self.shows) else None

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
