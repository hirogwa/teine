var models = require('./models.js');
var views = require('./views.js');

var mediaManagerTemplate = require('./templates/media-manager.html');
var MediaManagerView = Backbone.View.extend({
    el: $('#media-manager'),

    events: {
        'change input#media-manager-file-input': 'changeInputFile',
        'click button#upload-media': 'uploadMedia'
    },

    initialize: function() {
        _.bindAll(this, 'render',
                  'changeInputFile', 'uploadMedia');
        this.template = mediaManagerTemplate;

        var self = this;
        $.ajax({
            url: '/media-list',
            success: function(data) {
                self.mediaCollection =
                    models.MediaCollection.existingCollection(data);
                self.mediaListView =
                    new views.MediaListView({
                        collection: self.mediaCollection
                    });
                self.render();
            },
            error: function(data) {
                console.log(data);
            }
        });
    },

    render: function(args) {
        var options = args || {};
        this.$el.html(this.template({
            inputFileName: options.inputFileName || '',
            buttonUploadState: options.inputFileName ? '' : 'disabled'
        }));
        this.$('#media-list').append(this.mediaListView.render().el);
        return this;
    },

    changeInputFile: function(e) {
        this.newFile = e.currentTarget.files[0];
        console.log(this.newFile);
        var file_size_upperbound = 80000000; // 80MB
        if (this.newFile.size < file_size_upperbound) {
            this.render({
                inputFileName: this.newFile.name
            });
        } else {
            console.log('warn');
        }
        return this;
    },

    uploadMedia: function(e) {
        if (this.newFile) {
            var data = new FormData();
            data.append('file', this.newFile);
            var media = new models.Media({
                data: data
            });
            media.upload().then(function(result) {
                console.log(result);
            });
        }
    }
});

module.exports = {
    MediaManagerView: MediaManagerView
};
