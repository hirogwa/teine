var Personality = Backbone.Model;

var People = Backbone.Collection.extend({
    model: Personality,

    addPersonalityFromTwitter: function(params) {
        if (this.every(function(p) {
            return !p.get('twitter') ||
                p.get('twitter').screen_name !== params.screen_name;
        })) {
            params.profile_image_url = params.profile_image_url
                .replace('_normal', '_400x400');
            this.add(new Personality({
                twitter: params
            }));
        }
    }
});

module.exports = {
    Personality: Personality,
    People: People
};
