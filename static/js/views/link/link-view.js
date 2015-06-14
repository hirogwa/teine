var linkViewTemplate = require('./link-view.html');
var LinkView = Backbone.View.extend({
    events: {
        'click button#remove-link': 'removeLink'
    },

    initialize: function() {
        _.bindAll(this, 'render');
        this.template = linkViewTemplate;
    },

    render: function() {
        this.$el.html(this.template({
            url: this.model.get('url'),
            title: this.model.get('title')
        }));
        return this;
    },

    removeLink: function(e) {
        this.model.collection.remove(this.model);
        return this;
    }
});

module.exports = {
    LinkView: LinkView
};
