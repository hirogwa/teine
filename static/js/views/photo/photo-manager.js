var notify = require('../utils/notification.js').notify;
var dialog = require('../utils/dialog.js').dialog;

var models = require('../../models/photo.js');

var views = require('../photo/photo-list-view.js');

var PhotoManagerView = Backbone.View.extend({
    el: $('#photo-manager'),

    events: {
        'change input#photo-manager-file-input': 'changeInputFile'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'refreshListView', 'deletePhoto',
                  'changeInputFile');

        this.template = require('./photo-manager.html');

        var self = this;
        this.refreshListView();
    },

    render: function() {
        this.$el.html(this.template({
        }));
        this.$('#photo-list').append(this.photoListView.render().el);
        return this;
    },

    refreshListView: function() {
        var self = this;
        models.PhotoCollection.load().then(function(result) {
            self.collection = result;
            self.photoListView = new views.PhotoListView({
                collection: self.collection,
                delegates: {
                    deletePhoto: self.deletePhoto
                }
            });
            self.render();
        }, function(reason) {
        });
    },

    deletePhoto: function(photo_id, filename) {
        var self = this;
        dialog.confirmDelete(filename, function() {
            var notifyDeleting = notify.deleting(filename);
            models.Photo.destroy(photo_id).then(function(result) {
                notifyDeleting.close();
                self.refreshListView();
            }, function(reason) {
                notify.error();
            });
        });
    },

    changeInputFile: function(e) {
        var self = this;
        var file = e.currentTarget.files[0];
        $(e.currentTarget).val('');
        var notifyUploading = notify.uploading(file.name);
        models.Photo.newFile(file).upload().then(function(result) {
            notifyUploading.close();
            notify.uploaded(file.name);
            self.refreshListView();
        }, function(reason) {
            notify.error();
        });
        return this;
    }
});

module.exports = {
    PhotoManagerView: PhotoManagerView
};
