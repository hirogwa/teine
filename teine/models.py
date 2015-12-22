import datetime
import uuid

from teine import dynamo


class Show():
    table_name = "Show"
    hash_key = 'show_id'
    secondary_indexes = [('owner_user_id',)]

    def __eq__(self, another):
        return self.__dict__ == another.__dict__

    def __init__(self, show_id, owner_user_id, title='', author='', tagline='',
                 description='', show_host_ids=[], image_id='',
                 language='en-us', **kwargs):
        self.show_id = show_id
        self.owner_user_id = owner_user_id
        self.title = title
        self.author = author
        self.tagline = tagline
        self.description = description
        self.show_host_ids = show_host_ids
        self.image_id = image_id
        self.language = language

    @classmethod
    def load(cls, show_id):
        """
        Sets up a new in-memory 'Show' by accessing database for
        an existing show_id
        """
        rs = dynamo.query(cls.table_name, 'show_id', show_id)
        for val in rs:
            return cls(**val)
        return None

    @classmethod
    def create(cls, show_id, owner_user_id, title='', author='', tagline='',
               description='', show_host_ids=[], image_id='',
               language='en-us'):
        """
        Constructs an unsaved 'Show' instance.
        To persist the data, you need to call 'Show.save' on the instance.
        """
        return cls(show_id=show_id,
                   owner_user_id=owner_user_id,
                   title=title, author=author, tagline=tagline,
                   description=description, show_host_ids=show_host_ids,
                   image_id=image_id, language=language)

    def save(self):
        """
        Saves this 'Show' data to database
        """
        dynamo.update(self.table_name, self.export())
        return self

    def delete(self):
        """
        Deletes this Show from database
        """
        dynamo.delete(self.table_name, show_id=self.show_id)
        return True

    def export(self, expand=[]):
        """
        Returns dictionary representing this 'Show' instance

        To expand internal substructures, pass the attribute names
        in the expand parameter
        """
        ret = {
            'show_id': self.show_id,
            'owner_user_id': self.owner_user_id,
            'title': self.title,
            'author': self.author,
            'tagline': self.tagline,
            'description': self.description,
            'show_host_ids': self.show_host_ids,
            'image_id': self.image_id,
            'language': self.language
        }

        if 'show_hosts' in expand:
            ret['show_hosts'] = list(map(
                lambda x: Personality.load(x).export(),
                self.show_host_ids or []))
        if 'image' in expand:
            ret['image'] = Photo.load(
                self.image_id).export() if self.image_id else None

        return ret

    def episodes(self):
        """
        Returns the list of all episodes belonging to this 'Show'
        """
        return Episode.load_all(self.show_id)


class Episode():
    table_name = 'Episode'
    hash_key = 'episode_id'
    secondary_indexes = [('show_id', 'input_datetime')]

    def __eq__(self, another):
        return self.__dict__ == another.__dict__

    def __init__(self, episode_id, show_id, title='', summary='',
                 description='', media_id=None, guest_ids=[], links=[],
                 status=None, **kwargs):
        """
        Sets up a new in-memory 'Episode' by accessing database for
        an existing episode_id
        """
        self.episode_id = episode_id
        self.show_id = show_id
        self.title = title
        self.summary = summary
        self.description = description
        self.media_id = media_id
        self._media = None
        self.guest_ids = guest_ids
        self.guests = []
        self.links = links
        self.status = status

    @staticmethod
    def _convert_links(val):
        val['links'] = list(map(lambda x: Link(**x), val.get('links') or []))
        return val

    @classmethod
    def load(cls, episode_id):
        """
        Sets up a new in-memory 'Episode' by accessing database for
        an existing episode_id
        """
        rs = dynamo.query(cls.table_name, 'episode_id', episode_id)
        for val in rs:
            return cls._adjust_db_data(val)
        return None

    @classmethod
    def _adjust_db_data(cls, rs):
        return cls(**(cls._convert_links(rs)))

    @classmethod
    def load_all(cls, show_id):
        """
        Returns the list of all Episodes belonging to the passed show_id
        """
        rs = dynamo.scan(cls.table_name,
                         show_id, 'show_id' if show_id else None)
        return [cls._adjust_db_data(val) for val in rs]

    @classmethod
    def create(cls, episode_id, show_id, title='', summary='', description='',
               media_id=None, guest_ids=[], links=[], status=None):
        """
        Constructs an unsaved 'Episode' instance.
        To persist the data, you need to call 'Episode.save' on the instance
        """
        return cls(episode_id, show_id, title, summary, description, media_id,
                   guest_ids, links, status)

    def export(self, expand=[]):
        """
        Returns dictionary representing this 'Episode' instance

        To expand internal substructures, pass the attribute names
        in the expand parameter
        """
        ret = {
            'episode_id': self.episode_id,
            'show_id': self.show_id,
            'title': self.title,
            'summary': self.summary,
            'description': self.description,
            'media_id': self.media_id,
            'guest_ids': self.guest_ids,
            'status': self.status
        }

        if 'media' in expand:
            ret['media'] = Media.load(
                self.media_id).export() if self.media_id else None
        if 'guests' in expand:
            if not self.guests:
                self.guests = map(
                    lambda x: Personality.load(x), self.guest_ids)
            ret['guests'] = list(map(lambda x: x.export(), self.guests))
        if 'links' in expand:
            ret['links'] = list(map(lambda x: x.export(), self.links))
        return ret

    def save(self):
        """
        Saves this 'Episode' data to database
        """
        dynamo.update(self.table_name, self.export(expand=['media', 'links']))
        return self

    def delete(self):
        """
        Deletes this Episode from database
        """
        dynamo.delete(self.table_name, episode_id=self.episode_id)
        return True


class Link():
    def __init__(self, url, title):
        """
        Returns a new in-memory 'Link' instance
        """
        self.url = url
        self.title = title

    def export(self):
        """
        Returns the dictionary representation of this Link
        """
        return {
            'url': self.url,
            'title': self.title
        }


class Media():
    table_name = 'Media'
    hash_key = 'media_id'
    secondary_indexes = [('owner_user_id',)]

    def __eq__(self, another):
        return self.__dict__ == another.__dict__

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
    def create(cls, **kwargs):
        """
        Constructs an (unsaved) 'Media' instance.
        To persist the data, you need to call 'Media.save' on the instance.
        """
        return cls(str(uuid.uuid4()), **kwargs)

    @classmethod
    def load(cls, media_id):
        """
        Sets up a new in-memory 'Media' by accessing database for
        an existing media_id
        """
        rs = dynamo.query(cls.table_name, 'media_id', media_id)
        for val in rs:
            return Media(**val)
        return None

    @classmethod
    def load_all(cls, user_id):
        """
        Returns the list of all Media objects owned by a specific user
        """
        rs = dynamo.scan(cls.table_name, user_id, 'owner_user_id')
        return map(lambda x: Media(**x), rs)

    def export(self, episode_summary=False):
        """
        Returns the dictionary representation of this Media

        Set episode_summary True to pass the summary of the associated episode
        """
        ret = {
            'media_id': self.media_id,
            'owner_user_id': self.owner_user_id,
            'episode_id': self.episode_id,
            'name': self.name,
            'content_type': self.content_type,
            'size': str(self.size),
            'datetime': self.datetime
        }
        if episode_summary and self.episode_id:
            ret['episode'] = Episode.load(self.episode_id).export()
        return ret

    def save(self):
        """
        Saves this Media data to database
        """
        data = self.export()
        data['datetime'] = datetime.datetime.utcnow().isoformat()
        dynamo.update(self.table_name, data)
        return self

    def delete(self):
        """
        Deletes this Media data from database
        """
        dynamo.delete(self.table_name, media_id=self.media_id)
        return self


class Photo():
    table_name = 'Photo'
    hash_key = 'photo_id'

    def __eq__(self, another):
        return self.__dict__ == another.__dict__

    def __init__(self, photo_id, owner_user_id, thumbnail_id, filename,
                 size=None, content_type=None, datetime=None, **kwargs):
        self.photo_id = photo_id
        self.owner_user_id = owner_user_id
        self.thumbnail_id = thumbnail_id
        self.filename = filename
        self.size = size
        self.content_type = content_type
        self.datetime = datetime

    @classmethod
    def load(cls, photo_id):
        """
        Sets up a new in-memory 'Photo' by accessing database for
        an existing photo_id
        """
        rs = dynamo.query(cls.table_name, 'photo_id', photo_id)
        for val in rs:
            return cls(**val)
        return None

    @classmethod
    def create(cls, photo_id, owner_user_id, thumbnail_id, filename,
               size=None, content_type=None, datetime=None):
        """
        Constructs an (unsaved) 'Photo' instance.
        To persist the data, you need to call 'Photo.save' on the instance.
        """
        return cls(photo_id, owner_user_id, thumbnail_id, filename, size,
                   content_type, datetime)

    @classmethod
    def load_all(cls, user_id):
        """
        Returns the list of all Photo objects owned by a specific user
        """
        rs = dynamo.scan(cls.table_name, user_id, 'owner_user_id')
        return map(lambda x: cls(**x), rs)

    def export(self):
        """
        Returns the dictionary representation of this Photo
        """
        return self.__dict__

    def save(self):
        """
        Saves this Photo to database
        """
        dynamo.update(self.table_name, self.export())
        return self

    def delete(self):
        """
        Deletes this Photo from database
        """
        dynamo.delete(self.table_name, photo_id=self.photo_id)
        return True


class Personality():
    table_name = 'Personality'
    hash_key = 'personality_id'
    secondary_indexes = [('show_id', 'twitter_screen_name',)]

    def __eq__(self, another):
        return self.__dict__ == another.__dict__

    def __init__(self, personality_id, show_id, twitter=None, **kwargs):
        self.personality_id = personality_id
        self.show_id = show_id
        self.twitter = twitter
        self.twitter_screen_name = (
            twitter.get('screen_name') if twitter else None)

    @classmethod
    def load(cls, personality_id):
        """
        Sets up a new in-memory 'Personality' by accessing database for
        an existing personality_id
        """
        rs = dynamo.query(cls.table_name, 'personality_id', personality_id)
        for val in rs:
            return cls(**val)
        return None

    @classmethod
    def find_by_twitter(cls, screen_name, show_id):
        """
        Like the 'load' method, but by twitter information instead of id
        """
        rs = dynamo.query(cls.table_name, 'show_id', show_id,
                          'twitter_screen_name', screen_name)
        for val in rs:
            return cls(**val)
        return None

    @classmethod
    def create_from_twitter(cls, personality_id, show_id, screen_name,
                            name='', description='', profile_image_url=None):
        """
        Constructs an (unsaved) 'Personality' instance.
        To persist the data, you need to call 'Personality.save'
        """
        return cls(personality_id=personality_id,
                   show_id=show_id,
                   twitter={'screen_name': screen_name,
                            'name': name,
                            'description': description,
                            'profile_image_url': profile_image_url})

    def export(self):
        """
        Returns the dictionary representation of this Personality
        """
        return {
            'personality_id': self.personality_id,
            'show_id': self.show_id,
            'twitter_screen_name': (
                self.twitter.get('screen_name') if self.twitter else None),
            'twitter': self.twitter
        }

    def save(self):
        """
        Saves this Personality to database
        """
        dynamo.update(self.table_name, self.export())
        return self

    def delete(self):
        '''
        Deletes this Personality from database
        '''
        dynamo.delete(self.table_name, personality_id=self.personality_id)
        return True


class User():
    table_name = 'User'
    hash_key = 'user_id'
    secondary_indexes = [('email',)]

    def __eq__(self, another):
        return self.__dict__ == another.__dict__

    def __init__(self, user_id, password, email, first_name='', last_name='',
                 show_ids=[]):
        self.user_id = user_id
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

        self.show_ids = show_ids

        self._is_authenticated = True
        self._is_active = True
        self._is_anonymous = False

    @classmethod
    def load(cls, user_id=None, email=None):
        """
        Sets up a new in-memory 'User' for an existing User instance
        either by user_id or email
        """
        if user_id:
            rs = dynamo.query(cls.table_name, 'user_id', user_id)
            for val in rs:
                return cls(**val)
            return None

        if email:
            rs = dynamo.query(cls.table_name, 'email', email)
            for val in rs:
                return cls(**val)
            return None
        return None

    @classmethod
    def create(cls, user_id, password, email, first_name, last_name):
        """
        Constructs an (unsaved) 'User' instance.
        To persist the data, you need to call 'User.save'
        """
        return cls(user_id, password, email, first_name, last_name)

    def primary_show_id(self):
        return self.show_ids[0] if len(self.show_ids) else None

    def export(self, expand_password=False):
        """
        Returns the dictionary representation of this User
        """
        result = {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'show_ids': self.show_ids
        }
        if expand_password:
            result['password'] = self.password
        return result

    def save(self):
        """
        Saves this User to database
        """
        dynamo.update(self.table_name, self.export(True))
        return self

    def delete(self):
        '''
        Deletes this User from database
        '''
        dynamo.delete(self.table_name, user_id=self.user_id)
        return True

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
