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
        'click button#remove-show-image': 'removeImage',
        'click button#save-show': 'saveShow'
    },

    initialize: function(args) {
        var options = args || {};
        _.bindAll(this, 'render', 'renderImage', 'saveShow',
                  'changeInputFile', 'removeImage');
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
            showDescription: this.show.get('description'),
            imageId: this.show.get('image_id'),
            language: {
                ja: this.show.get('language') === 'ja' ? 'selected' : '',
                en: this.show.get('language') === 'en-us' ? 'selected' : ''
            }
        }));
        this.$('#show-regular-hosts').append(this.peopleView.render().el);
        this.renderImage(this.show.get('image_id'));

        this.peopleView.postRender();

        return this;
    },

    renderImage: function(imageExists) {
        var elImage = this.$('#show-image').empty();
        var elButtonRemove = this.$('#show-image-button-remove').empty();
        if (imageExists) {
            elImage.append(
                '<img src="/show-image" height="150" width="150" />');
            elButtonRemove.append(
                '<button type="button" class="btn btn-sm btn-warning" ' +
                    'id="remove-show-image">' +
                    '<i class="fa fa-times"></i> Remove image' +
                    '</button>');
        }

        return this;
    },

    removeImage: function(e) {
        this.show.set({
            image_id: undefined
        });
        this.renderImage(false);
        return this;
    },

    changeInputFile: function(e) {
        var newFile = e.currentTarget.files[0];
        if (!newFile) {
            return this;
        }

        var notifyUploading =
            notify.doing('Uploading {}...'.replace('{}', newFile.name));

        var self = this;
        this.uploadingImage =  utils.uploadFile('/show-image', newFile)
            .then(function(result) {
                notifyUploading.close();
                notify.done('{} uploaded!'.replace('{}', newFile.name));
                self.renderImage(result.image_id);
                return Promise.resolve();
            }, function(reason) {
                notifyUploading.close();
                notify.error();
                return Promise.reject();
            });

        return this;
    },

    saveShow: function() {
        var uploadingImage = this.newImageFile ?
            this.uploadImage(this.newImageFile) : Promise.resolve({
                image_id: this.show.get('image_id')
            });

        var self = this;
        (this.uploadingImage || Promise.resolve({})).then(function(result) {
            self.show.set({
                image_id: result.image_id,
                title: $('#show-title').val(),
                tagline: $('#show-tagline').val(),
                description: $('#show-description').val(),
                language: $('#show-language').val()
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
