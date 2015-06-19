var Links = require('./link.js').Links;
var People = require('./personality.js').People;
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

Episode.existingData = function(input) {
    var guests = new People();
    input.guests.forEach(function(g) {
        if (g.twitter) {
            guests.addPersonalityFromTwitter(g.twitter);
        }
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
        media_id: input.media_id,
        media: input.media ? Media.existingData(input.media) : undefined,
        guests: guests,
        links: links,
        status: input.status
    });
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
        episodes.add(Episode.existingData(e));
    });
    return episodes;
};

module.exports = {
    Episode: Episode,
    Episodes: Episodes
};
