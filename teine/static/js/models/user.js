var User = Backbone.Model.extend({
    url: '/user',

    parse: function(data) {
        var user = data.user;
        return {
            user_id: user.user_id,
            first_name: user.first_name,
            last_name: user.last_name,
            email: user.email,
            show_ids: user.show_ids
        };
    },

    checkSignupValidity: function() {
        var self = this;
        return new Promise(function(resolve, reject) {
            $.ajax({
                url: '/validate-signup-entry',
                method: 'POST',
                dataType: 'json',
                data: {
                    user_id: self.get('user_id') || '',
                    email: self.get('email') || '',
                    password: self.get('password') || ''
                },
                success: function(data) {
                    resolve(data);
                },
                error: function(data) {
                    reject(data);
                }
            });
        });
    }
});

module.exports = {
    User: User
};
