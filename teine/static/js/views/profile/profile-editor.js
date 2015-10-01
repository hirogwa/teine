var notify = require('../utils/notification.js').notify;

var models = require('../../models/user.js');

var ProfileEditorView = Backbone.View.extend({
    el: $('#profile-editor'),

    events: {
        'input input#profile-first-name': 'inputFirstName',
        'input input#profile-last-name': 'inputLastName',
        'input input#profile-email': 'inputEmail',
        'click button#save-profile': 'saveProfile'
    },

    initialize: function(args) {
        _.bindAll(this, 'inputFirstName', 'inputLastName', 'inputEmail',
                  'saveProfile', 'render');
        this.template = require('./profile-editor.html');

        var self = this;
        if (args.user_id) {
            new models.User().fetch({
                success: function(model, resp, options) {
                    self.user = model;
                    self.render();
                },
                error: function(model, resp, options) {
                    notify.error();
                }
            });
        } else {
            this.user = new models.User();
            this.render();
        }
    },

    render: function() {
        this.$el.html(this.template({
            user: this.user
        }));
        return this;
    },

    inputFirstName: function(e) {
        this.user.set({ first_name: e.currentTarget.value });
    },

    inputLastName: function(e) {
        this.user.set({ last_name: e.currentTarget.value });
    },

    inputEmail: function(e) {
        this.user.set({ email: e.currentTarget.value });
    },

    saveProfile: function(e) {
        var n = notify.saving();
        return this.user.save().then(function(result) {
            if (result.result === 'success') {
                n.close();
                notify.saved();
            } else {
                n.close();
                notify.error();
            }
        }, function(reason) {
            n.close();
            notify.error();
        });
    }
});

module.exports = {
    ProfileEditorView: ProfileEditorView
};
