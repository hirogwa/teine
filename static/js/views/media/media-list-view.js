require('bootstrapNotify');
var models = {
    Media: require('../../models/media.js').Media
};

var mediaListViewTemplate = require('./media-list-view.html');
var MediaListView = Backbone.View.extend({
    events: {
        'click button.delete-media': 'deleteMedia'
    },

    initialize: function(options) {
        _.bindAll(this, 'render', 'deleteMedia');
        this.template = mediaListViewTemplate;

        this.deleteMediaDelegate =
            options.delegates && options.delegates.deleteMedia ?
            options.delegates.deleteMedia : function(){};
    },

    render: function(args) {
        var options = args || {};
        this.$el.html(this.template({
            mediaList: this.collection,
            showEpisode: options.kind === 'used',
            showDelete: options.kind === 'unused'
        }));
        return this;
    },

    deleteMedia: function(e) {
        this.deleteMediaDelegate(
            $(e.currentTarget).data('media-name'),
            $(e.currentTarget).data('media-id')
        );
    }
});

module.exports = {
    MediaListView: MediaListView
};
