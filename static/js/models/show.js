var People = require('./personality.js').People;

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
        show_hosts.addPersonalityFromTwitter(p.twitter);
    });

    s.set({
        show_id: input.show_id,
        title: input.title,
        tagline: input.tagline,
        description: input.description,
        show_hosts: show_hosts
    });
    return s;
};

module.exports = {
    Show: Show
};
