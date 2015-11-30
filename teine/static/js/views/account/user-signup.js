var models = {
    User: require('../../models/user.js').User
};

var notify = require('../utils/notification.js').notify;

var userSignupTemplate = require('./user-signup.html');
var UserSignupView = Backbone.View.extend({
    el: $('#user-signup-page'),

    events: {
        'click button#submit-signup': 'signup',
        'keyup input.signup-entry': 'keyupOnForm'
    },

    initialize: function(args) {
        _.bindAll(this, 'render', 'keyupOnForm', 'signup');
        this.template = userSignupTemplate;
        this.render();
    },

    render: function() {
        this.$el.html(this.template());
        return this;
    },

    keyupOnForm: function(event) {
        if (event.keyCode === 13) {
            return this.signup();
        }
    },

    signup: function() {
        var user_id = $('#input-user-name').val();
        var email = $('#input-email').val();
        var password = $('#input-password').val();

        if (!user_id) {
            notify.warn('Please enter username');
            return;
        }
        if (!email) {
            notify.warn('Please enter email address');
            return;
        }
        if (!password) {
            notify.warn('Password is required');
            return;
        }

        var user = new models.User({
            user_id: user_id,
            email: email,
            password: password
        });

        user.checkSignupValidity().then(function(result) {
            if (result.result === 'success') {
                user.save(null, {
                    success: function(model, response) {
                        window.location = '/profile';
                    },
                    error: function(model, xhr) {
                        notify.error();
                    }
                });
            } else {
                notify.error(result.message);
            }
        }, function(reason) {
            notify.error();
        });
    }
});
module.exports = {
    UserSignupView: UserSignupView
};
