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
        'change input#new-link-url': 'changeUrl'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'renderAdd',
                  'addLink', 'changeUrl',
                  'titleElement', 'urlElement');
        this.template = linkListViewTemplate;

        this.collection.on('add', this.renderAdd);
        this.collection.on('remove', this.render);
    },

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
    },

    changeUrl: function(e) {
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
            id: this.model.get('id'),
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

module.exports = {
    LinkListView: LinkListView,
    PersonalityView: PersonalityView,
    PersonalityListView: PersonalityListView,
    EpisodeListView: EpisodeListView,
    MediaListView: MediaListView
};
