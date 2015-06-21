var User = Backbone.Model.extend({
    url: '/profile-data'
});

User.load = function(username) {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '/profile-data',
            success: function(data) {
                if (data.result === 'success') {
                    var user = data.user;
                    resolve(new User({
                        user_id: user.user_id,
                        first_name: user.first_name,
                        last_name: user.last_name,
                        email: user.email,
                        show_ids: user.show_ids
                    }));
                } else {
                    reject();
                }
            },
            error: function(data) {
                reject();
            }
        });
    });
};

module.exports = {
    User: User
};
