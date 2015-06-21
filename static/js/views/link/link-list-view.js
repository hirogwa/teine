var dialog = require('../utils/dialog.js').dialog;

var utils = require('../../utils.js');

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
                  'addLink', 'inputUrl', 'checkUrl', 'checkUrlCollection',
                  'titleElement', 'urlElement');
        this.template = linkListViewTemplate;

        this.collection.on('add', this.render);
        this.collection.on('remove', this.render);
        this.pendingLink = new models.Link();
    },

    checkUrlCollection: function() {
        var self = this;
        this.collection.filter(function(l) {
            return !l.urlCheckStatus;
        }).forEach(function(l) {
            self.checkUrl(l.get('url')).then(function(result) {
                l.urlCheckStatus = 'found';
                l.trigger('change');
            }, function(result) {
                l.urlCheckStatus = result.status;
                l.trigger('change');
            });
        });
    },

    inputTitle: function(e) {
        this.pendingLink.set({
            title: e.currentTarget.value
        });
    },

    inputUrl: _.debounce(function(e) {
        var self = this;

        var onResolve = function(result) {
            var duplLink = self.collection.find(function(c) {
                return c.get('url') === result.url;
            });
            if (duplLink) {
                self.pendingLink.set({
                    url: result.url,
                    title: duplLink.get('title')
                });
                self.pendingLink.urlCheckStatus = 'duplicate';
                self.renderSelector(false);
            } else {
                self.pendingLink.set({
                    url: result.url,
                    title: result.title
                });
                self.pendingLink.urlCheckStatus = 'found';
                self.renderSelector();
            }
        };

        var onReject = function(result) {
            self.pendingLink.set({
                title: result.title
            });
            self.pendingLink.urlCheckStatus = result.status;
            self.renderSelector();
        };

        var urlValue = e.currentTarget.value;

        if (urlValue) {
            this.pendingLink.set({
                url: urlValue
            });
            this.pendingLink.urlCheckStatus = 'checking';
            this.renderSelector();

            var urls = utils.getUrls(this.pendingLink.get('url'));
            this.checkUrl(urls.ssl).then(function(sResult) {
                onResolve(sResult);
            }, function(r) {
                self.checkUrl(urls.nonssl).then(function(nonSResult) {
                    onResolve(nonSResult);
                }, function(r) {
                    self.checkUrl(urls.raw).then(function(rawResult) {
                        onResolve(rawResult);
                    }, function(rawReason) {
                        rawReason.url = utils.toHttpUrl(rawReason.url);
                        onReject(rawReason);
                    });
                });
            });
        } else {
            this.pendingLink.set({
                url: '',
                title: ''
            });
            this.pendingLink.urlCheckStatus = undefined;
            this.renderSelector();
        }
    }, 500),

    checkUrl: function(url) {
        var self = this;
        return new Promise(function(resolve, reject) {
            if (!url) {
                reject({
                    url: url
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
                        resolve({
                            url: url,
                            title: data.title
                        });
                    } else {
                        reject({
                            url: url,
                            status: 'invalid'
                        });
                    }
                },
                error: function(data) {
                    reject({
                        url: url,
                        status: 'error'
                    });
                }
            });
        });
    },

    render: function() {
        var self = this;
        this.$el.html(this.template());
        this.renderSelector();
        this.collection.models.forEach(function(l) {
            this.renderAdd(l);
        }, this);
        this.checkUrlCollection();
        return this;
    },

    renderAdd: function(l) {
        this.$('#external-link-list').append(new LinkView({
            model: l
        }).render().el);
        return this;
    },

    renderSelector: function(urlAddable) {
        var enableAddButton = urlAddable === undefined ?
            this.pendingLink.get('url') : urlAddable;

        this.urlElement().val(this.pendingLink.get('url'));
        this.titleElement().val(this.pendingLink.get('title'));

        if (enableAddButton) {
            this.$('#add-link').removeAttr('disabled');
        } else {
            this.$('#add-link').attr('disabled', true);
        }

        var msgEl = this.$('#url-check-status').empty();
        var checkStatus = this.pendingLink.urlCheckStatus;
        if (checkStatus === 'checking') {
            msgEl.append('checking...');
        } else if (checkStatus === 'found') {
            msgEl.append('found!');
        } else if (checkStatus === 'invalid') {
            msgEl.append('seems invalid');
        } else if (checkStatus === 'duplicate') {
            msgEl.append('you have it already!');
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
        var addFunc = function(checkStatus) {
            self.pendingLink.urlCheckStatus = checkStatus;
            self.pendingLink.set({
                url: utils.toHttpUrl(self.pendingLink.get('url'))
            });
            self.pendingLink.set({
                title: self.pendingLink.get('title') ||
                    self.pendingLink.get('url')
            });
            self.collection.add(self.pendingLink);
            self.pendingLink = new models.Link();
            self.renderSelector();
            self.urlElement().focus();
        };

        var urlCheckStatus = this.pendingLink.urlCheckStatus;
        if (urlCheckStatus === 'found') {
            addFunc(urlCheckStatus);
        } else {
            dialog.confirmInvalidUrl(
                this.pendingLink.get('url'), urlCheckStatus, addFunc);
        }

        return this;
    }
});

module.exports = {
    LinkListView: LinkListView,
};
