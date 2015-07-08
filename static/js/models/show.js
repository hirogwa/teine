var models = {
    People: require('./personality.js').People,
    Photo: require('./photo.js').Photo
};

var Show = Backbone.Model.extend({
    url: '/show',

    defaults: {
        show_hosts: new models.People()
    },

    parse: function(input) {
        var show_hosts = new models.People();

        if (input.show_hosts) {
            input.show_hosts.forEach(function(p) {
                show_hosts.addPersonalityFromTwitter(p.twitter);
            });
        }

        if (input.image) {
            this.image = new models.Photo(input.image);
        }

        return {
            show_id: input.show_id,
            title: input.title,
            author: input.author,
            tagline: input.tagline,
            description: input.description,
            image_id: input.image_id,
            language: input.language,
            show_hosts: show_hosts
        };
    }
});

module.exports = {
    Show: Show
};
