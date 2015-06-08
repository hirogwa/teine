var models = require('./models.js');
var views = require('./views.js');

var mediaManagerTemplate = require('./templates/media-manager.html');
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
                  'changeInputFile', 'uploadMedia',
                  'setUsedMedia', 'setUnusedMedia');
        this.template = mediaManagerTemplate;

        var self = this;
        models.MediaCollection.loadUnused().then(function(result) {
            self.mediaListView = new views.MediaListView({
                collection: result
            });
            self.render({
                tabStatusUnused: 'active'
            });
        }, function(reason){
            console.log('failed to initialize');
        });
    },

    render: function(args) {
        var options = args || {};
        if (!options.tabStatusUsed) {
            options.tabStatusUnused = 'active';
        }
        this.$el.html(this.template({
            inputFileName: this.newFile ? this.newFile.name : '',
            buttonUploadState: this.newFile ? '' : 'disabled',
            tabStatusUsed: options.tabStatusUsed,
            tabStatusUnused: options.tabStatusUnused
        }));
        this.$('#media-list').append(this.mediaListView.render().el);
        return this;
    },

    setUsedMedia: function(e) {
        var self = this;
        return models.MediaCollection.loadUsed().then(function(result) {
            self.mediaListView = new views.MediaListView({
                collection: result
            });
            self.render({
                tabStatusUsed: 'active'
            });
        }, function(reason){
            console.log(reason);
        });
    },

    setUnusedMedia: function(e) {
        var self = this;
        return models.MediaCollection.loadUnused().then(function(result) {
            self.mediaListView = new views.MediaListView({
                collection: result
            });
            self.render({
                tabStatusUnused: 'active'
            });
        }, function(reason) {
            console.log(reason);
        });
    },

    changeInputFile: function(e) {
        this.newFile = e.currentTarget.files[0];
        console.log(this.newFile);
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
            var data = new FormData();
            data.append('file', this.newFile);
            var media = new models.Media({
                data: data
            });
            media.upload().then(function(result) {
                self.setUnusedMedia();
                console.log(result);
            });
        }
    }
});

module.exports = {
    MediaManagerView: MediaManagerView
};
