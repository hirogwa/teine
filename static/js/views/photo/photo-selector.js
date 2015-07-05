var models = require('../../models/photo.js');

var notify = require('../utils/notification.js').notify;

var dialog = require('../utils/dialog.js').dialog;

var PhotoSelectorView = Backbone.View.extend({
    events: {
        'click a.select-photo': 'onSelectPhoto',
        'change #photo-selector-file-input': 'changeInputFile'
    },

    initialize: function(args) {
        var options = args || {};
        this.selectedPhoto = options.selectedPhoto;

        _.bindAll(this, 'onSelectPhoto', 'changeInputFile');
        this.template = require('./photo-selector.html');
        this.refreshCollection();
    },

    onSelectPhoto: function(e) {
        this.selectPhoto($(e.currentTarget).data('photo-id'));
    },

    selectPhoto: function(photoId) {
        var self = this;
        var selectIt = function() {
            self.selectedPhoto = self.collection.find(function(p) {
                return p.get('photo_id') === photoId;
            });
            self.selectedPhoto.selected = true;
        };

        if (this.selectedPhoto) {
            this.selectedPhoto.selected = false;
            if (this.selectedPhoto.get('photo_id') === photoId) {
                this.selectedPhoto = undefined;
            } else {
                selectIt();
            }
        } else {
            selectIt();
        }
        this.render();
    },

    refreshCollection: function() {
        var self = this;
        this.loadCollection = models.PhotoCollection.load().then(function(photoCollection) {
            if (self.selectedPhoto) {
                self.selectedPhoto = photoCollection.find(function(p) {
                    return p.equals(self.selectedPhoto);
                });
                self.selectedPhoto.selected = true;
            }
            self.collection = photoCollection;
            self.render();
            return Promise.resolve();
        }, function(reason) {
            return Promise.reject(reason);
        });

        return this.loadCollection;
    },

    changeInputFile: function(e) {
        var self = this;
        var file = e.currentTarget.files[0];
        $(e.currentTarget).val('');

        var notifyOptions = {
            element: 'photo-selector-notify'
        };
        var notifyUploading = notify.uploading(file.name, notifyOptions);
        models.Photo.upload(file).then(function(result) {
            notifyUploading.close();
            notify.uploaded(file.name, notifyOptions);
            self.selectedPhoto = result;
            self.refreshCollection();
        }, function(reason) {
            notify.error(notifyOptions);
        });
        return this;
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
                dialog.selector('Select image', self.$el, {
                    cancel: function() {
                        resolve();
                    },
                    done: function() {
                        resolve(self.selectedPhoto);
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
