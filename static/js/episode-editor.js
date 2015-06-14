var models = require('./models.js');
var views = require('./views.js');
var episodeEditorTemplate = require('./templates/episode-editor.html');

var EpisodeEditorView = Backbone.View.extend({
    el: $('#episode-editor'),

    events: {
        'change input#episode-title': 'changeTitle',
        'change input#episode-summary': 'changeSummary',
        'change textarea#episode-description': 'changeDescription',
        'change input#schedule-datetime': 'changeScheduleDatetime',

        'click button#add-personality': 'addPersonality',
    },

    initialize: function(args) {
        var options = args || {};
        _.bindAll(this, 'render',
                  'changeTitle', 'changeSummary', 'changeDescription',
                  'changeScheduleDatetime',
                  'addPersonality', 'setSelectedMedia',
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
                            media: data.media ? models.Media.existingData(data.media) : undefined
                        });
                    },
                    error: function(data) {
                        reject(data);
                    }
                });
            } else {
                resolve({
                    episode: new models.Episode()
                });
            }
        });

        var loadingMediaCollection = models.MediaCollection.loadUnused();

        Promise.all([
            loadingEpisode,
            loadingMediaCollection
        ]).then(function(results) {
            self.episode = results[0].episode;
            self.media = results[0].media;
            self.mediaCollection = results[1];

            self.peopleView = new views.PersonalityListView({
                collection: self.episode.get('guests')
            });
            self.linkListView = new views.LinkListView({
                collection: self.episode.get('links')
            });
            self.saveActionView = new views.EpisodeSaveActionView({
                delegates: {
                    saveDraft: self.saveDraft,
                    schedule: self.schedule,
                    publish: self.publish
                },
                status: self.episode.get('status')
            });

            if (self.media) {
                self.media.set({
                    'selector-selected': true
                });
                self.mediaCollection.unshift(self.media);
            }
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
        this.episode.get('guests').add(new models.Personality({
            twitter: $('#new-personality-twitter').val()
        }));
    },

    publish: function(e) {
        this.setSelectedMedia();
        this.episode.publish();
    },

    saveDraft: function(e) {
        this.setSelectedMedia();
        this.episode.saveDraft();
    },

    schedule: function(e, args) {
        var options = args || {};
        this.setSelectedMedia();
        this.episode.schedule(options.scheduled_date);
    },

    setSelectedMedia: function() {
        var media = this.mediaCollection.selectedMedia();
        this.episode.set({
            media_id: media ? media.get('media_id') : undefined
        });
        return this;
    }
});

module.exports = {
    EpisodeEditorView: EpisodeEditorView
};
