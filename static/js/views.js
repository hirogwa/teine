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
    },

    initialize: function() {
        _.bindAll(this, 'render', 'renderAdd', 'addLink');
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

    addLink: function(e) {
        this.collection.addLink({
            title: $('#new-link-title').val(),
            url: $('#new-link-url').val()
        });
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

module.exports = {
    LinkListView: LinkListView,
    PersonalityView: PersonalityView,
    PersonalityListView: PersonalityListView
};
