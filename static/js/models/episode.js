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

    publish: function() {
        this.saveType({
            saved_as: 'published'
        });
        this.save();
    },

    saveDraft: function() {
        this.saveType({
            saved_as: 'draft'
        });
        this.save();
    },

    schedule: function(scheduled_date) {
        this.saveType({
            saved_as: 'scheduled',
            schedule_date: scheduled_date
        });
        this.save();
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
