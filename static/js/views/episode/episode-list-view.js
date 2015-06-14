var models = {
    Episodes: require('../../models/episode.js').Episodes
};

var episodeListViewTemplate = require('./episode-list-view.html');
var EpisodeListView = Backbone.View.extend({
    el: $('#episode-list'),

    initialize: function() {
        _.bindAll(this, 'render');
        this.template = episodeListViewTemplate;

        var self = this;
        $.ajax({
            url: '/episodes',
            success: function(data) {
                console.log(data);
                self.collection = models.Episodes.existingList(data);
                self.render();
            },
            error: function(data) {
                console.log(data);
            }
        });
    },

    render: function() {
        this.$el.html(this.template({
            episodes: this.collection
        }));
        return this;
    }
});

module.exports = {
    EpisodeListView: EpisodeListView
};
