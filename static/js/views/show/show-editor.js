var utils = require('../../utils.js');

var views = {
    PersonalityListView: require('../personality/personality-list-view.js').PersonalityListView
};
var models = {
    Show: require('../../models/show.js').Show
};

var notify = require('../utils/notification.js').notify;

var showEditorTemplate = require('./show-editor.html');
var ShowEditorView = Backbone.View.extend({
    el: $('#show-editor'),

    events: {
        'change input#show-editor-image-input': 'changeInputFile',
        'click button#save-show': 'saveShow'
    },

    initialize: function(args) {
        var options = args || {};
        _.bindAll(this, 'render', 'saveShow', 'uploadImage', 'changeInputFile');
        this.template = showEditorTemplate;

        var self = this;
        new Promise(function(resolve, reject) {
            if (options.show_id) {
                $.ajax({
                    url: '/show',
                    data: {
                        show_id: options.show_id
                    },
                    dataType: 'json',
                    success: function(data) {
                        self.show = models.Show.existingData(data);
                        resolve(data);
                    },
                    error: function(data) {
                        reject(data);
                    }
                });
            } else {
                self.show = new models.Show();
                resolve();
            }
        }).then(function() {
            self.peopleView = new views.PersonalityListView({
                collection: self.show.get('show_hosts')
            });
            self.render();
        }, function() {
            console.log('oops');
        });
    },

    render: function() {
        this.$el.html(this.template({
            showTitle: this.show.get('title'),
            showTagline: this.show.get('tagline'),
            showDescription: this.show.get('description')
        }));
        this.$('#show-regular-hosts').append(this.peopleView.render().el);

        this.peopleView.postRender();

        return this;
    },

    changeInputFile: function(e) {
        this.newImageFile = e.currentTarget.files[0];
        var element = this.$('#show-editor-file-name').empty();
        if (this.newImageFile) {
            element.append(this.newImageFile.name);
        }
        return this;
    },

    uploadImage: function(fileObj) {
        if (!fileObj) {
            return Promise.resolve();
        }

        var data = new FormData();
        data.append('file', fileObj);

        var notifyUploading = notify.doing(
            'Uploading {}...'.replace('{}', fileObj.name));
        return utils.uploadData('/upload-show-image', data)
            .then(function(result) {
                notifyUploading.close();
                if (result.result === 'success') {
                    notify.done('{} uploaded!'.replace('{}', fileObj.name));
                } else {
                    notify.error();
                }
                return result;
            }, function(reason) {
                notifyUploading.close();
                notify.error();
                return reason;
            });
    },

    saveShow: function() {
        var uploadingImage = this.uploadImage(this.newImageFile);
        console.log(uploadingImage);

        var self = this;
        uploadingImage.then(function(result) {
            self.show.set({
                image_id: result.image_id,
                title: $('#show-title').val(),
                tagline: $('#show-tagline').val(),
                description: $('#show-description').val()
            });

            var saving = notify.saving();
            self.show.save(null, {
                success: function(model, response) {
                    if (response.result === 'success') {
                        saving.close();
                        notify.saved();
                    } else {
                        notify.error();
                    }
                },
                error: function(model, xhr) {
                    notify.error();
                }
            });
        }, function(reason) {
        });
    }
});

module.exports = {
    ShowEditorView: ShowEditorView
};
