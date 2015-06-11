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
                 title='', summary='', description='',
                 media_id=None, guests=[], links=[], **kwargs):
        self.episode_id = episode_id
        self.show_id = show_id
        self.title = title
        self.summary = summary
        self.description = description
        self.media_id = media_id
        self.guests = guests
        self.links = links

    @classmethod
    def create_new(cls, show_id, **kwargs):
        kwargs['links'] = map(lambda x: Link(**x), kwargs.get('links'))
        return Episode(str(uuid.uuid4()), show_id, **kwargs)

    @classmethod
    def get_by_id(cls, episode_id):
        rs = dynamo.query(cls.table_name, episode_id__eq=episode_id)
        for val in rs:
            return cls.from_db(val)
        return None

    @classmethod
    def get_list(cls):
        rs = dynamo.scan(cls.table_name)
        return map(cls.from_db, rs)

    @classmethod
    def from_db(cls, val):
        # TODO show
        return Episode(val.get('episode_id'),
                       None,
                       title=val.get('title'),
                       summary=val.get('summary'),
                       description=val.get('description'),
                       media_id=val.get('media_id'),
                       guests=map(
                           lambda x: Personality(**x),
                           val.get('guests') or []),
                       links=map(
                           lambda x: Link(**x),
                           val.get('links') or []))

    def export(self):
        return {
            'episode_id': self.episode_id,
            'show_id': self.show_id,
            'title': self.title,
            'summary': self.summary,
            'description': self.description,
            'media_id': self.media_id,
            'guests': list(self.guests),
            'links': list(map(lambda x: x.export(), self.links))
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

    def __init__(self, media_id, owner_user, name='',
                 content_type=None, size=0, status=None):
        self.media_id = media_id
        self.owner_user = owner_user
        self.name = name
        self.content_type = content_type
        self.size = size
        self.status = status

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

    def associated_with_episode(self):
        return self.status != 'draft'

    def export(self):
        return {
            'media_id': self.media_id,
            'owner_user': self.owner_user,
            'name': self.name,
            'content_type': self.content_type,
            'size': str(self.size),
            'status': self.status
        }

    def save(self):
        dynamo.update(self.table_name, self.export())
        return self

    def delete(self):
        dynamo.delete(self.table_name, media_id=self.media_id)
        return self


class Personality():
    table_name = 'teine-Personality'

    def __init__(self, personality_id, show_id, twitter=None,
                 twitter_identity=None):
        self.personality_id = personality_id
        self.show_id = show_id
        self.twitter = twitter
        self.twitter_identity = twitter_identity

    @classmethod
    def create_from_twitter(cls, screen_name, show_id, twitter_identity,
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
        identity = TwitterIdentity.find_identity(screen_name)
        if identity:
            return cls.get_by_id(identity.personality_id)
        else:
            identity = TwitterIdentity.create_new(screen_name)
            personality = Personality.create_from_twitter(
                screen_name, show_id, identity, **kwargs)
            return (personality.save(True)
                    if create_when_not_found else personality)

    def save(self, save_identity=False):
        dynamo.update(self.table_name, self.export())
        if save_identity and self.twitter_identity:
            self.twitter_identity.save()
        return self

    def export(self):
        return {
            'personality_id': self.personality_id,
            'show_id': self.show_id,
            'twitter': self.twitter
        }


class TwitterIdentity():
    table_name = 'teine-PersonalityIdentityTwitter'

    def __init__(self, screen_name, personality_id):
        self.screen_name = screen_name
        self.personality_id = personality_id

    @classmethod
    def create_new(cls, screen_name):
        return TwitterIdentity(screen_name, str(uuid.uuid4()))

    @classmethod
    def find_identity(cls, screen_name):
        rs = dynamo.query(cls.table_name, screen_name__eq=screen_name)
        for val in rs:
            return TwitterIdentity(**val)
        return None

    def save(self):
        dynamo.update(self.table_name, self.export())
        return self

    def export(self):
        return {
            'screen_name': self.screen_name,
            'personality_id': self.personality_id
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
