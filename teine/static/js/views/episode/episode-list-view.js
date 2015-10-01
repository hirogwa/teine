var models = {
    Episode: require('../../models/episode.js').Episode,
    Episodes: require('../../models/episode.js').Episodes
};

var notify = require('../utils/notification.js').notify;
var dialog = require('../utils/dialog.js').dialog;
require('bootstrapNotify');

var episodeListViewTemplate = require('./episode-list-view.html');
var EpisodeListView = Backbone.View.extend({
    el: $('#episode-list'),

    events: {
        'click button#delete-episode': 'deleteEpisode'
    },

    initialize: function(args) {
        var options = args || {};
        _.bindAll(this, 'render', 'deleteEpisode', 'refreshCollection');
        this.template = episodeListViewTemplate;

        if (options && options.episodeSaved) {
            notify.saved('Episode saved!');
        }
        if (options && options.error) {
            notify.error();
        }

        this.refreshCollection();
    },

    render: function() {
        this.$el.html(this.template({
            episodes: this.collection
        }));
        return this;
    },

    refreshCollection: function() {
        var self = this;
        new models.Episodes().fetch({
            success: function(collection, resp, options) {
                self.collection = collection;
                self.render();
            },
            error: function(collection, resp, options) {
                notify.error();
            }
        });
    },

    deleteEpisode: function(e) {
        var self = this;

        var episodeId = $(e.currentTarget).data('episode-id');
        var episodeTitle = $(e.currentTarget).data('episode-title');

        var episode = this.collection.find(function(ep) {
            return ep.get('episode_id') === episodeId;
        });

        dialog.confirmDelete(episodeTitle, function() {
            var notifyDeleting = notify.doing(
                'Deleting "{}"...'.replace('{}', episodeTitle));

            episode.destroy({
                data: $.param({
                    episode_id: episode.get('episode_id')
                }),
                success: function(model, resp, options) {
                    notifyDeleting.close();
                    notify.deleted(episodeTitle);
                    self.refreshCollection();
                },
                error: function(model, resp, options) {
                    notifyDeleting.close();
                    notify.error();
                }
            });
        });
    }
});

module.exports = {
    EpisodeListView: EpisodeListView
};
