var personalityViewTemplate = require('./personality-view.html');
var PersonalityView = Backbone.View.extend({
    events: {
        'click button.remove-personality': 'removePersonality'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'removePersonality');
        this.template = personalityViewTemplate;
    },

    render: function() {
        this.$el.html(this.template({
            alias: this.model.get('alias'),
            name: this.model.get('name'),
            description: this.model.get('description'),
            profile_image_url: this.model.get('profile_image_url')
        }));
        return this;
    },

    removePersonality: function(e) {
        this.model.collection.remove(this.model);
        return this;
    }
});

module.exports = {
    PersonalityView: PersonalityView
};
