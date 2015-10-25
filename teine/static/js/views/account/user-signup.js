var userSignupTemplate = require('./user-signup.html');
var UserSignupView = Backbone.View.extend({
    el: $('#user-signup-page'),

    initialize: function(args) {
        _.bindAll(this, 'render');
        this.template = userSignupTemplate;
        this.render();
    },

    render: function() {
        this.$el.html(this.template());
        return this;
    }
});

module.exports = {
    UserSignupView: UserSignupView
};
