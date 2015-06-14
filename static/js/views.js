var models = require('./models.js');

var linkViewTemplate = require('./link-view.html');
var LinkView = Backbone.View.extend({
    events: {
        'click button#remove-link': 'removeLink'
    },

    initialize: function() {
        _.bindAll(this, 'render');
        this.template = linkViewTemplate;
    },

    render: function() {
        this.$el.html(this.template({
            url: this.model.get('url'),
            title: this.model.get('title')
        }));
        return this;
    },

    removeLink: function(e) {
        this.model.collection.remove(this.model);
        return this;
    }
});

var linkListViewTemplate = require('./link-list-view.html');
var LinkListView = Backbone.View.extend({
    events: {
        'click button#add-link': 'addLink',
        'input input#new-link-url': 'inputUrl'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'renderAdd',
                  'addLink', 'inputUrl', 'checkUrl',
                  'titleElement', 'urlElement');
        this.template = linkListViewTemplate;

        this.collection.on('add', this.renderAdd);
        this.collection.on('remove', this.render);
    },

    inputUrl: function(e) {
        this.checkUrl(e);
    },

    checkUrl: _.debounce(function(e) {
        var self = this;
        var url = e.currentTarget.value;
        $.ajax({
            url: '/link-info',
            method: 'GET',
            data: {
                url: url
            },
            success: function(data) {
                if (data.result === 'success') {
                    self.titleElement().val(data.title);
                } else {
                    console.log(data.reason);
                }
            },
            error: function(data) {
                console.log(data);
            }
        });
    }, 500),

    render: function() {
        this.$el.html(this.template());
        this.collection.models.forEach(function(l) {
            this.renderAdd(l);
        }, this);
        return this;
    },

    renderAdd: function(l) {
        this.$('#external-link-list').append(new LinkView({
            model: l
        }).render().el);
        return this;
    },

    urlElement: function() {
        return $('#new-link-url');
    },

    titleElement: function() {
        return $('#new-link-title');
    },

    addLink: function(e) {
        this.collection.addLink({
            title: this.titleElement().val(),
            url: this.urlElement().val()
        });
        this.titleElement().val('');
        this.urlElement().val('');
        return this;
    }
});

var personalityViewTemplate = require('./personality-view.html');
var PersonalityView = Backbone.View.extend({
    events: {
        'click button.remove-personality': 'removePersonality'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'removePersonality');
        this.template = personalityViewTemplate;
    },

    render: function() {
        this.$el.html(this.template({
            alias: this.model.get('alias'),
            name: this.model.get('name'),
            description: this.model.get('description'),
            profile_image_url: this.model.get('profile_image_url')
        }));
        return this;
    },

    removePersonality: function(e) {
        this.model.collection.remove(this.model);
        return this;
    }
});

var personalityListViewTemplate = require('./personality-list-view.html');
var PersonalityListView = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render', 'renderAdd', 'postRender', 'renderFull',
                  'formatTwitterUserResult', 'formatTwitterUserSelection');
        this.template = personalityListViewTemplate;
        this.collection.on('add', this.renderAdd);
        this.collection.on('remove', this.renderFull);
        this.collection.on('reset', this.renderFull);
    },

    renderFull: function() {
        return this.render().postRender();
    },

    render: function() {
        this.$el.html(this.template());
        this.collection.forEach(function(p) {
            this.renderAdd(p);
        }, this);

        return this;
    },

    renderAdd: function(p) {
        this.$('#personality-list').append(new PersonalityView({
            model: p
        }).render().el);
        return this;
    },

    postRender: function() {
        var self = this;
        var twitterUserSelect = '#select-twitter-user';
        $(twitterUserSelect).select2({
            ajax: {
                url: '/twitter-user-search',
                dataType: 'json',
                delay: 500,
                data: function(params) {
                    return {
                        q: params.term
                    };
                },
                processResults: function(data, page) {
                    return {
                        results: data
                    };
                }
            },
            minimumInputLength: 2,
            escapeMarkup: function(markup) {
                return markup;
            },
            templateResult: function(result) {
                return self.formatTwitterUserResult(result);
            },
            templateSelection: function(item) {
                return self.formatTwitterUserSelection(item);
            }
        });

        $(twitterUserSelect).on('change', function(e) {
            var item = $(twitterUserSelect).select2('data')[0];
            self.collection.addPersonalityFromTwitter(item);
        });

        return this;
    },

    formatTwitterUserResult: function(result) {
        if (result.loading) {
            return result.text;
        }
        return '<div>' +
            '<img src="' + result.profile_image_url + '"/>' +
            '<span>' + result.screen_name + ' ' + result.name + '</span>' +
            '</div>';
    },

    formatTwitterUserSelection: function(item) {
        //return 'Type in name to add...';
        return '';
    }
});

var episodeListViewTemplate = require('./templates/episode-list-view.html');
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

var episodeSaveActionViewTemplate =
    require('./templates/episode-save-action-view.html');
var EpisodeSaveActionView = Backbone.View.extend({
    events: {
        'change input#episode-save-option-draft': 'selectDraftOption',
        'change input#episode-save-option-schedule': 'selectScheduleOption',
        'change input#episode-save-option-publish': 'selectPublishOption',
        'change input#scheduled-date': 'changeScheduledDate',
        'click button#save-draft': 'saveDraft',
        'click button#schedule': 'schedule',
        'click button#publish': 'publish'
    },

    initialize: function(options) {
        _.bindAll(this, 'render', 'saveDraft', 'schedule', 'publish',
                  'changeScheduledDate',
                  'selectDraftOption',
                  'selectScheduleOption',
                  'selectPublishOption');
        this.template = episodeSaveActionViewTemplate;
        if (options && options.delegates) {
            this.delegates = {
                saveDraft: options.delegates.saveDraft || function() {},
                schedule: options.delegates.schedule || function() {},
                publish: options.delegates.publish || function() {}
            };
        }
        if (options && options.status) {
            console.log(options);
            this.savedAs = options.status.saved_as;
            this.scheduleDate = options.status.schedule_date;
        }
        this.savedAs = this.savedAs || 'draft';
        if (!this.scheduleDate) {
            var today = new Date();
            this.scheduleDate = 'yyyy-mm-dd'
                .replace('yyyy', today.getFullYear())
                .replace('mm', this.formatTwoDigits(today.getMonth() + 1))
                .replace('dd', this.formatTwoDigits(today.getDate()));
        }
        this.render();
    },

    formatTwoDigits: function(n) {
        return n < 10 ? '0{}'.replace('{}', n) : n;
    },

    render: function() {
        this.$el.html(this.template({
            draftSelected: this.savedAs === 'draft',
            scheduleSelected: this.savedAs === 'scheduled',
            publishSelected: this.savedAs === 'published',
            scheduleDate: this.scheduleDate
        }));
        return this;
    },

    selectDraftOption: function(e) {
        this.savedAs = 'draft';
        return this.render();
    },

    selectScheduleOption: function(e) {
        this.savedAs = 'scheduled';
        return this.render();
    },

    selectPublishOption: function(e) {
        this.savedAs = 'published';
        return this.render();
    },

    changeScheduledDate: function(e) {
        var dateValue = e.currentTarget.value;
        if (!dateValue) {
            e.currentTarget.valueAsDate = new Date();
        }
        this.scheduleDate = e.currentTarget.value;
    },

    saveDraft: function(e) {
        this.delegates.saveDraft(e);
        return this;
    },

    schedule: function(e) {
        this.delegates.schedule(e, {
            scheduled_date: $('#scheduled-date').val()
        });
        return this;
    },

    publish: function(e) {
        this.delegates.publish(e);
        return this;
    }
});

var mediaListViewTemplate = require('./templates/media-list-view.html');
var MediaListView = Backbone.View.extend({
    events: {
        'click a.delete-media': 'deleteMedia'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'deleteMedia');
        this.template = mediaListViewTemplate;
    },

    render: function() {
        this.$el.html(this.template({
            mediaList: this.collection
        }));
        return this;
    },

    deleteMedia: function(e) {
        models.Media.destroy($(e.currentTarget).data('media-id'));
    }
});

var mediaSelectorViewTemplate = require('./templates/media-selector-view.html');
var MediaSelectorView = Backbone.View.extend({
    events: {
        'click button.media-selector-select': 'selectMedia',
        'click button.media-selector-deselect': 'deselectMedia'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'selectMedia');
        this.template = mediaSelectorViewTemplate;
    },

    render: function() {
        this.$el.html(this.template({
            collection: this.collection
        }));
        return this;
    },

    selectMedia: function(e) {
        var targetId = $(e.currentTarget).data('media-id');
        this.collection.forEach(function(m) {
            m.set({
                'selector-selected': m.get('media_id') === targetId
            });
        });
        return this.render();
    },

    deselectMedia: function(e) {
        this.collection.forEach(function(m) {
            m.set({
                'selector-selected': false
            });
        });
        return this.render();
    }
});

module.exports = {
    LinkListView: LinkListView,
    PersonalityView: PersonalityView,
    PersonalityListView: PersonalityListView,
    EpisodeListView: EpisodeListView,
    EpisodeSaveActionView: EpisodeSaveActionView,
    MediaListView: MediaListView,
    MediaSelectorView: MediaSelectorView
};
