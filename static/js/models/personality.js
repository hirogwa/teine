var Personality = Backbone.Model;

var People = Backbone.Collection.extend({
    model: Personality,

    addPersonality: function(params) {
        this.add(new Personality({
            alias: params.alias,
            name: params.name,
            description: params.description,
            profile_image_url: params.profile_image_url
                .replace('_normal', '_400x400')
        }));
    },

    addPersonalityFromTwitter: function(params) {
        params.alias = params.screen_name;
        this.addPersonality(params);
    }
});

module.exports = {
    Personality: Personality,
    People: People
};
