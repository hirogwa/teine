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

        'click button#upload-episode-audio': 'uploadEpisodeAudio',

        'click button#add-personality': 'addPersonality',
        'click button#publish': 'publish',
        'click button#save-draft': 'saveDraft',
        'click button#schedule': 'schedule'
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
        new Promise(function(resolve, reject) {
            if (options.episode_id) {
                $.ajax({
                    url: '/episode',
                    data: {
                        episode_id: options.episode_id
                    },
                    dataType: 'json',
                    success: function(data) {
                        self.episode = models.Episode.existingData(data);
                        resolve(data);
                    },
                    error: function(data) {
                        reject(data);
                    }
                });
            } else {
                self.episode = new models.Episode();
                resolve();
            }
        }).then(function() {
            self.peopleView = new views.PersonalityListView({
                collection: self.episode.get('people')
            });
            self.linkListView = new views.LinkListView({
                collection: self.episode.get('links')
            });
            self.render();
        }, function() {
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

        this.peopleView.postRender();

        return this;
    },

    uploadEpisodeAudio: function(e) {
        var file = $('#episode-audio')[0].files[0];
        if (file) {
            var data = new FormData();
            data.append('file', file);

            var media = new models.Media({
                data: data
            });

            media.upload();
        }
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
