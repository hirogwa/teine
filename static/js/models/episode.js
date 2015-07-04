var Link = require('./link.js').Link;
var Links = require('./link.js').Links;
var People = require('./personality.js').People;
var Personality = require('./personality.js').Personality;
var Media = require('./media.js').Media;

var Episode = Backbone.Model.extend({
    url: '/episode',

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
    }
});

Episode.load = function(episodeId) {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '/episode',
            data: {
                episode_id: episodeId
            },
            dataType: 'json',
            success: function(data) {
                if (data.result === 'success') {
                    resolve(Episode.fromData(data.episode));
                } else {
                    reject(data);
                }
            },
            error: function(data) {
                reject(data);
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

Episode.fromData = function(episode) {
    var media = episode.media ? new Media(episode.media) : undefined;
    delete episode.media;

    var guests = new People();
    if (episode.guests) {
        episode.guests.forEach(function(g) {
            guests.add(new Personality(g));
        });
        episode.guests = guests;
    }

    var links = new Links();
    if (episode.links) {
        episode.links.forEach(function(l) {
            links.add(new Link(l));
        });
        episode.links = links;
    }

    var ep = new Episode(episode);
    ep.media = media;

    return ep;
};

Episode.destroy = function(episodeId) {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '/episode/' + episodeId,
            method: 'DELETE',
            success: function(data) {
                resolve(data);
            },
            error: function(data) {
                reject(data);
            }
        });
    });
};

var Episodes = Backbone.Collection.extend({
    model: Episode
});

Episodes.existingList = function(input) {
    var episodes = new Episodes();
    input.forEach(function(e) {
        episodes.add(Episode.fromData(e));
    });
    return episodes;
};

module.exports = {
    Episode: Episode,
    Episodes: Episodes
};
