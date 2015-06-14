var LinkView = require('./link-view.js').LinkView;

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

module.exports = {
    LinkListView: LinkListView,
};
