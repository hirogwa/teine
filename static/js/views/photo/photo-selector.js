var models = require('../../models/photo.js');

var notify = require('../utils/notification.js').notify;

var dialog = require('../utils/dialog.js').dialog;

var PhotoSelectorView = Backbone.View.extend({
    events: {
        'click a.select-photo': 'selectPhoto',
        'change #photo-selector-file-input': 'changeInputFile'
    },

    initialize: function() {
        _.bindAll(this, 'selectPhoto', 'changeInputFile');
        this.template = require('./photo-selector.html');
        this.refreshCollection();
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

    refreshCollection: function() {
        var self = this;
        this.loadCollection = models.PhotoCollection.load().then(function(result) {
            self.collection = result;
            self.render();
            return Promise.resolve();
        }, function(reason) {
            return Promise.reject(reason);
        });
    },

    changeInputFile: function(e) {
        var self = this;
        var file = e.currentTarget.files[0];
        $(e.currentTarget).val('');

        var notifyOptions = {
            element: 'photo-selector-notify'
        };
        var notifyUploading = notify.uploading(file.name, notifyOptions);
        models.Photo.newFile(file).upload().then(function(result) {
            notifyUploading.close();
            notify.uploaded(file.name, notifyOptions);
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
