var models = {
    Episode: require('../../models/episode.js').Episode,
    Media: require('../../models/media.js').Media,
    MediaCollection: require('../../models/media.js').MediaCollection,
    Personality: require('../../models/personality.js').Personality
};

var views = {
    PersonalityListView: require('../personality/personality-list-view.js').PersonalityListView,
    LinkListView: require('../link/link-list-view.js').LinkListView,
    EpisodeSaveActionView: require('../episode/episode-save-action-view.js').EpisodeSaveActionView,
    MediaSelectorView: require('../media/media-selector-view.js').MediaSelectorView
};

var notify = require('../utils/notification.js').notify;

var episodeEditorTemplate = require('./episode-editor.html');

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
                  'addPersonality', 'selectMedia', 'deselectMedia',
                  'publish', 'saveDraft', 'schedule', 'saveAndRedirect');
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
                        var episode = models.Episode.existingData(data.episode);
                        var media = data.media && !options.copy_mode ?
                            models.Media.existingData(data.media) : undefined;
                        if (options.copy_mode) {
                            episode.set({
                                episode_id: undefined,
                                title: 'Copy of {}'
                                    .replace('{}', episode.get('title'))
                            });
                        }

                        resolve({
                            episode: episode,
                            media: media
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
                collection: self.mediaCollection,
                delegates: {
                    selectMedia: self.selectMedia,
                    deselectMedia: self.deselectMedia
                }
            });
            self.render();
        }, function(reason) {
            console.log('failed to initialize episode editor');
            console.log(reason);
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

    saveAndRedirect: function(savePromise) {
        savePromise.then(function(result) {
            window.location.replace('/episode-list?notify=episodeSaved');
        }, function(reason) {
            notify.error();
        });
    },

    publish: function(e) {
        this.saveAndRedirect(this.episode.publish());
    },

    saveDraft: function(e) {
        this.saveAndRedirect(this.episode.saveDraft());
    },

    schedule: function(e, args) {
        var options = args || {};
        this.saveAndRedirect(this.episode.schedule(options.scheduled_date));
    },

    selectMedia: function(mediaId) {
        this.episode.set({
            media_id: mediaId
        });
    },

    deselectMedia: function() {
        this.episode.set({
            media_id: undefined
        });
    }
});

module.exports = {
    EpisodeEditorView: EpisodeEditorView
};
