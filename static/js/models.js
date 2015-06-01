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

var People = Backbone.Collection.extend({
    model: Personality,

    addPersonalityFromTwitter: function(params) {
        this.add(new Personality({
            source: 'twitter',
            id: params.screen_name,
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

module.exports = {
    Media: Media,
    Link: Link,
    Links: Links,
    Personality: Personality,
    People: People,
    Episode: Episode
};
