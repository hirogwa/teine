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
        new models.User({
            user_id: $('#input-user-name').val(),
            email: $('#input-email').val(),
            password: $('#input-password').val()
        }).save(null, {
            success: function(model, response) {
                window.location = '/profile';
            },
            error: function(model, xhr) {
                notify.error();
            }
        });
    }
});
module.exports = {
    UserSignupView: UserSignupView
};
