var models = {
    Media: require('../../models/media.js').Media
};
var mediaListViewTemplate = require('./media-list-view.html');
var MediaListView = Backbone.View.extend({
    events: {
        'click a.delete-media': 'deleteMedia'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'deleteMedia');
        this.template = mediaListViewTemplate;
    },

    render: function() {
        this.$el.html(this.template({
            mediaList: this.collection
        }));
        return this;
    },

    deleteMedia: function(e) {
        models.Media.destroy($(e.currentTarget).data('media-id'));
    }
});

module.exports = {
    MediaListView: MediaListView
};
