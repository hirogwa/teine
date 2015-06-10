var models = require('./models.js');
var views = require('./views.js');
var episodeEditorTemplate = require('./templates/episode-editor.html');

var EpisodeEditorView = Backbone.View.extend({
    el: $('#episode-editor'),

    events: {
        'change input#episode-title': 'changeTitle',
        'change input#episode-summary': 'changeSummary',
        'change input#episode-description': 'changeDescription',
        'change input#schedule-datetime': 'changeScheduleDatetime',

        'click button#add-personality': 'addPersonality',
    },

    initialize: function(args) {
        var options = args || {};
        _.bindAll(this, 'render',
                  'changeTitle', 'changeSummary', 'changeDescription',
                  'changeScheduleDatetime',
                  'addPersonality',
                  'publish', 'saveDraft', 'schedule');
        this.template = episodeEditorTemplate;

        var self = this;
        var loadingEpisode = new Promise(function(resolve, reject) {
            if (options.episode_id) {
                $.ajax({
                    url: '/episode',
                    data: {
                        episode_id: options.episode_id
                    },
                    dataType: 'json',
                    success: function(data) {
                        resolve({
                            episode: models.Episode.existingData(data.episode),
                            media: models.Media.existingData(data.media)
                        });
                    },
                    error: function(data) {
                        reject(data);
                    }
                });
            } else {
                self.episode = new models.Episode();
                resolve();
            }
        });

        var loadingMediaCollection = models.MediaCollection.loadUnused();

        Promise.all([
            loadingEpisode,
            loadingMediaCollection
        ]).then(function(result) {
            self.episode = result[0].episode;
            self.media = result[0].media;
            self.mediaCollection = result[1];

            self.peopleView = new views.PersonalityListView({
                collection: self.episode.get('people')
            });
            self.linkListView = new views.LinkListView({
                collection: self.episode.get('links')
            });
            self.saveActionView = new views.EpisodeSaveActionView({
                delegates: {
                    saveDraft: self.saveDraft,
                    schedule: self.schedule,
                    publish: self.publish
                }
            });

            self.media.set({
                'selector-selected': true
            });
            self.mediaCollection.unshift(self.media);
            self.mediaSelectorView = new views.MediaSelectorView({
                collection: self.mediaCollection
            });
            self.render();
        }, function(reason) {
            console.log('failed to initialize episode editor');
        });
    },

    render: function() {
        this.$el.html(this.template({
            episodeTitle: this.episode.get('title'),
            episodeSummary: this.episode.get('summary'),
            episodeDescription: this.episode.get('description')
        }));
        this.$('#episode-personality-list').append(this.peopleView.render().el);
        this.$('#episode-external-links').append(this.linkListView.render().el);
        this.$('#media-selector-view')
            .append(this.mediaSelectorView.render().el);
        this.$('#episode-save-action-view')
            .append(this.saveActionView.render().el);

        this.peopleView.postRender();

        return this;
    },

    changeTitle: function(e) {
        this.episode.set({
            title: e.currentTarget.value
        });
    },

    changeSummary: function(e) {
        this.episode.set({
            summary: e.currentTarget.value
        });
    },

    changeDescription: function(e) {
        this.episode.set({
            description: e.currentTarget.value
        });
    },

    changeScheduleDatetime: function(e) {
        this.episode.set({
            scheduledAt: e.currentTarget.value
        });
    },

    addPersonality: function(e) {
        this.episode.get('people').add(new models.Personality({
            twitter: $('#new-personality-twitter').val()
        }));
    },

    publish: function(e) {
        this.episode.publish();
    },

    saveDraft: function(e) {
        this.episode.saveDraft();
    },

    schedule: function(e) {
        this.episode.schedule();
    }
});

module.exports = {
    EpisodeEditorView: EpisodeEditorView
};
