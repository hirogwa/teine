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
            twitterUser: this.model.get('twitter')
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
