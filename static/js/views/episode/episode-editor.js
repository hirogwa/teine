var models = {
    Episode: require('../../models/episode.js').Episode,
    Media: require('../../models/media.js').Media,
    MediaCollection: require('../../models/media.js').MediaCollection,
    Personality: require('../../models/personality.js').Personality
};

var views = {
    PersonalityListView: require('../personality/personality-list-view.js')
        .PersonalityListView,
    LinkListView: require('../link/link-list-view.js').LinkListView,
    EpisodeSaveActionView: require('../episode/episode-save-action-view.js')
        .EpisodeSaveActionView,
    AudioSelector: require('../media/audio-selector.js').AudioSelector
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
        'click button#open-audio-selector': 'openAudioSelector'
    },

    initialize: function(args) {
        var options = args || {};
        _.bindAll(this, 'render',
                  'changeTitle', 'changeSummary', 'changeDescription',
                  'changeScheduleDatetime', 'openAudioSelector', 'renderAudio',
                  'addPersonality',
                  'publish', 'saveDraft', 'schedule', 'saveAndRedirect');
        this.template = episodeEditorTemplate;

        var loadingEpisode = function() {
            if (!options.episode_id) {
                return Promise.resolve(new models.Episode());
            }

            if (options.copy_mode) {
                return models.Episode.loadCopy(options.episode_id);
            } else {
                return models.Episode.load(options.episode_id);
            }
        };

        var self = this;
        Promise.all([
            loadingEpisode(),
            models.MediaCollection.loadUnused()
        ]).then(function(results) {
            self.episode = results[0];
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

            if (self.episode.media) {
                self.episode.media.set({
                    'selector-selected': true
                });
                self.mediaCollection.unshift(self.episode.media);
            }
            self.render();
        }, function(reason) {
            notify.error();
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
        this.$('#episode-save-action-view')
            .append(this.saveActionView.render().el);
        this.renderAudio();

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

    renderAudio: function() {
        var audioEl = this.$('#episode-selected-audio');
        audioEl.empty();
        if (this.episode.media) {
            audioEl.append('<span>{}</span>'
                           .replace('{}', this.episode.media.get('name')))
                .append('<audio id="selected-audio"><source type="{0}" src="/media/{1}"/></audio>'
                        .replace('{0}', this.episode.media.get('content_type'))
                        .replace('{1}', this.episode.media.get('media_id')));

            $('#selected-audio').mediaelementplayer();
        }
    },

    openAudioSelector: function(e) {
        var self = this;
        return new views.AudioSelector({
            selectedAudio: this.episode.media,
            targetEpisodeId: this.episode.get('episode_id')
        }).showDialog().then(function(media) {
            self.episode.media = media;
            self.episode.set({
                media_id: media ? media.get('media_id') : undefined
            });
            self.renderAudio();
        }, function(reason) {
            notify.error();
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
    }
});

module.exports = {
    EpisodeEditorView: EpisodeEditorView
};
