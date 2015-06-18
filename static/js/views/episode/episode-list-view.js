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
        $.ajax({
            url: '/episodes',
            success: function(data) {
                self.collection = models.Episodes.existingList(data);
                self.render();
            },
            error: function(data) {
                console.log(data);
            }
        });
    },

    deleteEpisode: function(e) {
        var self = this;

        var episodeId = $(e.currentTarget).data('episode-id');
        var episodeTitle = $(e.currentTarget).data('episode-title');

        dialog.confirmDelete(episodeTitle, function() {
            var notifyDeleting = notify.doing(
                'Deleting "{}"...'.replace('{}', episodeTitle));

            models.Episode.destroy(episodeId).then(function(result) {
                notifyDeleting.close();
                if (result.result === 'success') {
                    notify.done(
                        '"{}" deleted!'.replace('{}', episodeTitle));
                    self.refreshCollection();
                } else {
                    notify.error();
                }
            }, function(reason) {
                notifyDeleting.close();
                notify.error();
                console.log('failed to delete episode');
                console.log(reason);
            });
        });
    }
});

module.exports = {
    EpisodeListView: EpisodeListView
};
