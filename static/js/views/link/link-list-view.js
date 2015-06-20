var dialog = require('../utils/dialog.js').dialog;

var models = require('../../models/link.js');

var LinkView = require('./link-view.js').LinkView;

var linkListViewTemplate = require('./link-list-view.html');
var LinkListView = Backbone.View.extend({
    events: {
        'click button#add-link': 'addLink',
        'input input#new-link-url': 'inputUrl',
        'input input#new-link-title': 'inputTitle'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'renderAdd', 'renderSelector',
                  'addLink', 'inputUrl', 'checkUrl',
                  'titleElement', 'urlElement');
        this.template = linkListViewTemplate;

        this.collection.on('add', this.renderAdd);
        this.collection.on('remove', this.render);
        this.pendingLink = new models.Link();
    },

    inputTitle: function(e) {
        this.pendingLink.set({
            title: e.currentTarget.value
        });
    },

    inputUrl: _.debounce(function(e) {
        this.pendingLink.set({
            url: e.currentTarget.value
        });

        this.renderSelector(this.pendingLink.get('url'), 'checking');

        var self = this;
        this.checkUrl(this.pendingLink.get('url')).then(function(result) {
            self.titleElement().val(result);
            self.pendingLink.set({
                title: result,
                status: 'found'
            });
            self.renderSelector(true, 'found');
        }, function(result) {
            self.pendingLink.set({
                status: result.status
            });
            self.renderSelector(result.addable, result.status);
        });
    }, 500),

    checkUrl: function(url) {
        var self = this;
        return new Promise(function(resolve, reject) {
            if (!url) {
                reject({
                    addable: false
                });
            }

            if (self.collection && self.collection.find(function(c) {
                return c.get('url') === url;
            })) {
                reject({
                    addable: false,
                    status: 'duplicate'
                });
            }

            $.ajax({
                url: '/link-info',
                method: 'GET',
                data: {
                    url: url
                },
                success: function(data) {
                    if (data.result === 'success') {
                        resolve(data.title);
                    } else {
                        reject({
                            addable: true,
                            status: 'invalid'
                        });
                    }
                },
                error: function(data) {
                    reject({
                        addable: true,
                        status: 'error'
                    });
                }
            });
        });
    },

    render: function() {
        this.$el.html(this.template());
        this.renderSelector();
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

    renderSelector: function(enableAddButton, checkStatus) {
        if (enableAddButton) {
            this.$('#add-link').removeAttr('disabled');
        } else {
            this.$('#add-link').attr('disabled', true);
        }

        var msgEl = this.$('#url-check-status').empty();
        if (checkStatus === 'checking') {
            msgEl.append('checking...');
        } else if (checkStatus === 'found') {
            msgEl.append('found!');
        } else if (checkStatus === 'invalid') {
            msgEl.append('seems invalid');
        } else if (checkStatus === 'duplicate') {
            msgEl.append('you have added it already!');
        }

        return this;
    },

    urlElement: function() {
        return $('#new-link-url');
    },

    titleElement: function() {
        return $('#new-link-title');
    },

    addLink: function(e) {
        if (!this.urlElement().val()) {
            return this;
        }

        var self = this;
        var addFunc = function() {
            self.collection.add(self.pendingLink.set({
                title: self.pendingLink.get('title') ||
                    self.pendingLink.get('url')
            }));
            self.titleElement().val('');
            self.urlElement().val('');
            self.renderSelector(false);
            self.pendingLink = new models.Link();
        };

        if (this.pendingLink.get('status') === 'found') {
            addFunc();
        } else {
            dialog.confirmInvalidUrl(this.pendingLink.get('url'), addFunc);
        }

        return this;
    }
});

module.exports = {
    LinkListView: LinkListView,
};
