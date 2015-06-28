var utils = require('../../utils.js');

var views = {
    PersonalityListView: require('../personality/personality-list-view.js').PersonalityListView,
    PhotoSelectorView: require('../photo/photo-selector.js').PhotoSelectorView
};
var models = {
    Show: require('../../models/show.js').Show
};

var notify = require('../utils/notification.js').notify;

var showEditorTemplate = require('./show-editor.html');
var ShowEditorView = Backbone.View.extend({
    el: $('#show-editor'),

    events: {
        'click button#save-show': 'saveShow',
        'click button#open-photo-selector': 'openPhotoSelector',
        'click #remove-show-image': 'removeShowImage'
    },

    initialize: function(args) {
        var options = args || {};
        _.bindAll(this, 'render', 'renderImage', 'saveShow',
                  'openPhotoSelector', 'removeShowImage');
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
            notify.error();
        });
    },

    render: function() {
        this.$el.html(this.template({
            show: this.show,
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

    renderImage: function() {
        var photo = this.show.image;
        var elImage = this.$('#show-image').empty();
        var elButtonRemove = this.$('#show-image-button-remove').empty();

        if (photo) {
            elImage.append('<img src="/photo/{}" />'
                           .replace('{}', photo.get('thumbnail_id')));
            elButtonRemove.append(
                '<button type="button" class="btn btn-sm btn-warning" ' +
                    'id="remove-show-image">' +
                    '<i class="fa fa-times"></i> Remove' +
                    '</button>');
        }
        return this;
    },

    removeShowImage: function(e) {
        this.show.image = undefined;
        this.show.set({
            image_id: undefined
        });
        this.renderImage();
    },

    openPhotoSelector: function(e) {
        var self = this;
        new views.PhotoSelectorView().showDialog().then(function(result) {
            self.show.image = result;
            self.show.set({
                image_id: result ? result.get('photo_id') : undefined
            });
            self.renderImage();
        }, function(reason) {
            notify.error();
        });
    },

    saveShow: function() {
        var self = this;
        self.show.set({
            title: $('#show-title').val(),
            author: $('#show-author').val(),
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
    }
});

module.exports = {
    ShowEditorView: ShowEditorView
};
