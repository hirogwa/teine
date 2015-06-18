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
        'click button#save-show': 'saveShow'
    },

    initialize: function(args) {
        var options = args || {};
        _.bindAll(this, 'render', 'saveShow');
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

    saveShow: function() {
        this.show.set({
            title: $('#show-title').val(),
            tagline: $('#show-tagline').val(),
            description: $('#show-description').val()
        });
        var saving = notify.saving();
        this.show.save(null, {
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
