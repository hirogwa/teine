var models = require('../../models/photo.js');

var PhotoSelectorView = Backbone.View.extend({
    events: {
        'click a.select-photo': 'selectPhoto'
    },

    initialize: function() {
        _.bindAll(this, 'selectPhoto');
        this.template = require('./photo-selector.html');

        var self = this;
        this.loadCollection = models.PhotoCollection.load().then(function(result) {
            self.collection = result;
            self.render();
            return Promise.resolve();
        }, function(reason) {
            return Promise.reject(reason);
        });
    },

    selectPhoto: function(e) {
        this.selectedPhoto = this.collection.forEach(function(p) {
            p.selected = false;
        }).find(function(p) {
            return p.get('photo_id') === $(e.currentTarget).data('photo-id');
        });
        if (this.selectedPhoto) {
            this.selectedPhoto.selected = true;
        }
        this.render();
    },

    render: function() {
        this.$el.html(this.template({
            photos: this.collection
        }));
    },

    showDialog: function(title) {
        var self = this;
        return this.loadCollection.then(function(result) {
            return new Promise(function(resolve, reject) {
                bootbox.dialog({
                    title: title || 'Select image',
                    message: self.$el,
                    onEscape: function() {
                        resolve();
                    },
                    buttons: {
                        cancel: {
                            label: 'Cancel',
                            className: 'btn-default',
                            callback: function() {
                                resolve();
                            }
                        },
                        done: {
                            label: 'Done',
                            className: 'btn-primary',
                            callback: function() {
                                resolve(self.selectedPhoto);
                            }
                        }
                    }
                });
            });
        }, function(reason) {
            return Promise.reject(reason);
        });
    }
});

module.exports = {
    PhotoSelectorView: PhotoSelectorView
};
