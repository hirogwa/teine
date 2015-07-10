var User = Backbone.Model.extend({
    url: '/profile-data',

    parse: function(data) {
        var user = data.user;
        return {
            user_id: user.user_id,
            first_name: user.first_name,
            last_name: user.last_name,
            email: user.email,
            show_ids: user.show_ids
        };
    }
});

module.exports = {
    User: User
};
