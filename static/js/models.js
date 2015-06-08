var Media = Backbone.Model.extend({
    destroy: function() {
        var self = this;
        return new Promise(function(resolve, reject) {
            $.ajax({
                url: '/delete-media',
                data: {
                    media_id: self.get('media_id')
                },
                dataType: 'json',
                method: 'POST',
                success: function(data) {
                    resolve(data);
                },
                error: function(data) {
                    reject(data);
                }
            });
        });
    },

    upload: function() {
        var self = this;
        return new Promise(function(resolve, reject) {
            $.ajax({
                url: '/upload-media',
                data: self.get('data'),
                cache: false,
                processData: false,
                contentType: false,
                method: 'POST',
                success: function(data) {
                    console.log(data);
                    resolve(data);
                },
                error: function(data) {
                    console.log(data);
                    reject(data);
                }
            });
        });
    }
});

Media.existingData = function(input) {
    return new Media({
        media_id: input.media_id,
        name: input.name,
        size: input.size,
        contentType: input.content_type,
        status: input.status
    });
};

var MediaCollection = Backbone.Collection.extend({
    model: Media
});

MediaCollection.existingCollection = function(input) {
    var c = new MediaCollection();
    input.forEach(function(m) {
        c.add(Media.existingData(m));
    });
    return c;
};

var Link = Backbone.Model;

var Links  = Backbone.Collection.extend({
    model: Link,

    addLink: function(params) {
        this.add(new Link({
            url: params.url,
            title: params.title
        }));
    }
});

var Personality = Backbone.Model;

var People = Backbone.Collection.extend({
    model: Personality,

    addPersonality: function(params) {
        this.add(new Personality({
            source: params.source,
            alias: params.screen_name || params.alias,
            name: params.name,
            description: params.description,
            profile_image_url: params.profile_image_url
                .replace('_normal', '_400x400')
        }));
    },

    addPersonalityFromTwitter: function(params) {
        params.source = 'twitter';
    }
});

var Episode = Backbone.Model.extend({
    url: '/episode',

    defaults: {
        links: new Links(),
        people: new People()
    },

    saveType: function(input) {
        this.set({
            savedAs: input
        });
    },

    publish: function() {
        this.saveType('published');
        this.save();
    },

    saveDraft: function() {
        this.saveType('draft');
        this.save();
    },

    schedule: function() {
        this.saveType('scheduled');
        this.save();
    }
});

Episode.existingData = function(input) {
    var guests = new People();
    input.guests.forEach(function(p) {
        guests.addPersonality(p);
    });
    var links = new Links();
    input.links.forEach(function(l) {
        links.addLink(l);
    });

    return new Episode({
        episode_id: input.episode_id,
        title: input.title,
        summary: input.summary,
        description: input.description,
        people: guests,
        links: links
    });
};

var Episodes = Backbone.Collection.extend({
    model: Episode
});

Episodes.existingList = function(input) {
    var episodes = new Episodes();
    input.forEach(function(e) {
        episodes.add(Episode.existingData(e));
    });
    return episodes;
};

var Show = Backbone.Model.extend({
    url: '/show',

    defaults: {
        show_hosts: new People()
    }
});

Show.existingData = function(input) {
    var s = new Show();
    var show_hosts = new People();
    input.show_hosts.forEach(function(p) {
        show_hosts.addPersonality(p);
    });
    var episodes = new Episodes();
    input.episodes.forEach(function(e) {
        episodes.add(Episode.existingData(e));
    });

    s.set({
        show_id: input.show_id,
        title: input.title,
        tagline: input.tagline,
        description: input.description,
        show_hosts: show_hosts,
        episodes: episodes
    });
    return s;
};

module.exports = {
    Show: Show,
    Media: Media,
    MediaCollection: MediaCollection,
    Link: Link,
    Links: Links,
    Personality: Personality,
    People: People,
    Episode: Episode,
    Episodes: Episodes
};
