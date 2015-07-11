var Link = require('./link.js').Link;
var Links = require('./link.js').Links;
var People = require('./personality.js').People;
var Personality = require('./personality.js').Personality;
var Media = require('./media.js').Media;

var Episode = Backbone.Model.extend({
    url: '/episode',

    idAttribute: 'episode_id',

    defaults: {
        links: new Links(),
        guests: new People()
    },

    saveType: function(input) {
        this.set({
            status: input
        });
    },

    savePromise: function() {
        var self = this;
        return new Promise(function(resolve, reject) {
            self.save(null, {
                success: function(model, response) {
                    if (response.result === 'success') {
                        resolve(response);
                    } else {
                        reject(response);
                    }
                },
                error: function(model, xhr) {
                    reject(xhr);
                }
            });
        });
    },

    publish: function() {
        this.saveType({
            saved_as: 'published'
        });
        return this.savePromise();
    },

    saveDraft: function() {
        this.saveType({
            saved_as: 'draft'
        });
        return this.savePromise();
    },

    schedule: function(scheduled_date) {
        this.saveType({
            saved_as: 'scheduled',
            schedule_date: scheduled_date
        });
        return this.savePromise();
    },

    parse: function(data) {
        var episode = data.episode;

        var media = episode.media ? new Media(episode.media) : undefined;
        delete episode.media;

        var guests = new People();
        if (episode.guests) {
            episode.guests.forEach(function(g) {
                guests.add(new Personality(g));
            });
        }
        episode.guests = guests;

        var links = new Links();
        if (episode.links) {
            episode.links.forEach(function(l) {
                links.add(new Link(l));
            });
        }
        episode.links = links;

        this.media = media;

        return {
            show_id: episode.show_id,
            episode_id: episode.episode_id,
            title: episode.title,
            summary: episode.summary,
            description: episode.description,
            guests: episode.guests,
            links: episode.links,
            status: episode.status,
        };
    }
});

Episode.load = function(episodeId) {
    return new Promise(function(resolve, reject) {
        new Episode().fetch({
            data: $.param({
                episode_id: episodeId
            }),
            success: function(model, resp, options) {
                resolve(model);
            },
            error: function(model, resp, options) {
                reject();
            }
        });
    });
};

Episode.loadCopy = function(episodeId) {
    return Episode.load(episodeId).then(function(episode) {
        episode.set({
            episode_id: undefined,
            title: 'Copy of {}'.replace('{}', episode.get('title'))
        });
        episode.media = undefined;
        return Promise.resolve(episode);
    });
};

var Episodes = Backbone.Collection.extend({
    model: Episode,
    url: '/episodes',
});

module.exports = {
    Episode: Episode,
    Episodes: Episodes
};
