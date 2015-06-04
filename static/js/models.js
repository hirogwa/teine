var Media = Backbone.Model.extend({
    upload: function() {
        var self = this;
        $.ajax({
            url: '/media',
            data: self.get('data'),
            cache: false,
            processData: false,
            contentType: false,
            method: 'POST',
            success: function(data) {
                console.log(data);
            },
            error: function(data) {
                console.log(data);
            }
        });
    }
});

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

Personality.existingData = function(input) {
    return new Personality({
        alias: input.alias,
        name: input.name,
        description: input.description,
        profile_image_url: input.profile_image_url
    });
};

var People = Backbone.Collection.extend({
    model: Personality,

    addPersonalityFromTwitter: function(params) {
        this.add(new Personality({
            source: 'twitter',
            alias: params.screen_name,
            name: params.name,
            description: params.description,
            profile_image_url: params.profile_image_url
                .replace('_normal', '_400x400')
        }));
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
    var e =  new Episode();
    // TODO
    return e;
};

var Episodes = Backbone.Collection.extend({
    model: Episode
});

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
        show_hosts.add(Personality.existingData(p));
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
    Link: Link,
    Links: Links,
    Personality: Personality,
    People: People,
    Episode: Episode
};
