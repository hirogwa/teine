var models = {
    Media: require('../../models/media.js').Media,
    MediaCollection: require('../../models/media.js').MediaCollection
};
var views = {
    MediaListView: require('../media/media-list-view.js').MediaListView
};

var notify = require('../utils/notification.js').notify;
var dialog = require('../utils/dialog.js').dialog;
require('bootstrapNotify');

var mediaManagerTemplate = require('./media-manager.html');
var MediaManagerView = Backbone.View.extend({
    el: $('#media-manager'),

    events: {
        'change input#media-manager-file-input': 'changeInputFile',
        'click button#upload-media': 'uploadMedia',
        'click a#show-used-media': 'setUsedMedia',
        'click a#show-unused-media': 'setUnusedMedia'
    },

    initialize: function() {
        _.bindAll(this, 'render',
                  'changeInputFile', 'uploadMedia', 'deleteMedia',
                  'resetMediaListView', 'setUsedMedia', 'setUnusedMedia');
        this.template = mediaManagerTemplate;

        var self = this;
        models.MediaCollection.loadUnused().then(function(result) {
            self.resetMediaListView(result);
            self.render({
                kind: 'unused'
            });
        }, function(reason){
            console.log('failed to initialize');
        });
    },

    render: function(args) {
        var options = args || {};
        options.kind = options.kind || 'used';
        this.$el.html(this.template({
            inputFileName: this.newFile ? this.newFile.name : '',
            buttonUploadState: this.newFile ? '' : 'disabled',
            tabStatusUsed: options.kind === 'used' ? 'active' : '',
            tabStatusUnused: options.kind === 'unused' ? 'active' : ''
        }));
        this.$('#media-list').append(this.mediaListView.render({
            kind: options.kind
        }).el);
        return this;
    },

    resetMediaListView: function(collection) {
        this.mediaListView = new views.MediaListView({
            collection: collection,
            delegates: {
                deleteMedia: this.deleteMedia
            }
        });
        return this;
    },

    deleteMedia: function(mediaName, mediaId) {
        var self = this;
        dialog.confirmDelete(mediaName, function() {
            var notifyDeleting = notify.doing(
                'Deleting {}...'.replace('{}', mediaName));

            models.Media.destroy(mediaId).then(function(result) {
                if (result.result === 'success') {
                    notifyDeleting.close();
                    notify.done(
                        '{} deleted!'.replace('{}', mediaName));
                    self.setUnusedMedia();
                }
            }, function(reason) {
                console.log('failed to delete media');
                console.log(reason);
            });
        });
    },

    setUsedMedia: function(e) {
        var self = this;
        return models.MediaCollection.loadUsed().then(function(result) {
            self.resetMediaListView(result);
            self.render({
                kind: 'used'
            });
        }, function(reason){
            console.log(reason);
        });
    },

    setUnusedMedia: function(e) {
        var self = this;
        return models.MediaCollection.loadUnused().then(function(result) {
            self.resetMediaListView(result);
            self.render({
                kind: 'unused'
            });
        }, function(reason) {
            console.log(reason);
        });
    },

    changeInputFile: function(e) {
        this.newFile = e.currentTarget.files[0];
        var file_size_upperbound = 80000000; // 80MB
        if (this.newFile.size < file_size_upperbound) {
            this.render();
        } else {
            console.log('warn');
        }
        return this;
    },

    uploadMedia: function(e) {
        var self = this;
        if (this.newFile) {
            var media = new models.Media({
                file: this.newFile
            });

            var notifyUploading = notify.doing(
                'Uploading {}...'.replace('{}', this.newFile.name));
            media.upload().then(function(result) {
                notifyUploading.close();
                if (result.result === 'success') {
                    notify.done(
                        '{} uploaded!'.replace('{}', self.newFile.name));
                    self.newFile = undefined;
                    self.setUnusedMedia();
                } else {
                    notify.error();
                }
            }, function(reason) {
                notifyUploading.close();
                notify.error();
                console.log('failed to upload media');
                console.log(reason);
            });
        }
    }
});

module.exports = {
    MediaManagerView: MediaManagerView
};
