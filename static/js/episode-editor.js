var models = require('./models.js');
var views = require('./views.js');
var episodeEditorTemplate = require('./templates/episode-editor.html');

var EpisodeEditorView = Backbone.View.extend({
    el: $('#episode-editor'),

    events: {
        'change input#episode-title': 'changeTitle',
        'change input#episode-summary': 'changeSummary',
        'change input#episode-description': 'changeDescription',
        'change input#episode-audio': 'changeAudio',
        'change input#schedule-datetime': 'changeScheduleDatetime',

        'click button#upload-episode-audio': 'uploadEpisodeAudio',

        'click button#add-personality': 'addPersonality',
        'click button#publish': 'publish',
        'click button#save-draft': 'saveDraft',
        'click button#schedule': 'schedule'
    },

    initialize: function() {
        _.bindAll(this, 'render',
                  'changeTitle', 'changeSummary', 'changeDescription',
                  'changeScheduleDatetime',
                  'addPersonality',
                  'publish', 'saveDraft', 'schedule');

        this.episode = new models.Episode();
        this.peopleView = new views.PersonalityListView({
            collection: this.episode.get('people')
        });
        this.linkListView = new views.LinkListView({
            collection: this.episode.get('links')
        });

        this.template = episodeEditorTemplate;
        this.render();
        console.log('init');
    },

    render: function() {
        this.$el.html(this.template({
            people: this.episode.get('people')
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
        console.log(file);
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

    changeAudio: function(e) {
        console.log(e);
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

new EpisodeEditorView();
