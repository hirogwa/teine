var linkViewTemplate = require('./link-view.html');
var LinkView = Backbone.View.extend({
    tagName: 'tr',

    events: {
        'click button#remove-link': 'removeLink',
        'click button#move-up-link': 'moveUpLink',
        'click button#move-down-link': 'moveDownLink'
    },

    initialize: function() {
        _.bindAll(this, 'render');
        this.template = linkViewTemplate;
        this.model.on('change', this.render);
    },

    render: function(e) {
        var index = this.model.collection.indexOf(this.model);
        this.$el.html(this.template({
            url: this.model.get('url'),
            title: this.model.get('title'),
            status: this.model.urlCheckStatus,
            uppable: index > 0,
            downable: index > -1 && index < this.model.collection.length - 1
        }));
        return this;
    },

    removeLink: function(e) {
        this.model.collection.remove(this.model);
        return this;
    },

    moveUpLink: function() {
        this.model.collection.moveUp(this.model);
        return this;
    },

    moveDownLink: function() {
        this.model.collection.moveDown(this.model);
        return this;
    }
});

module.exports = {
    LinkView: LinkView
};
