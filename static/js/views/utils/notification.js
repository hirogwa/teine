require('bootstrapNotify');

var notify = {
    saving: function(message) {
        return this.doing(message || 'Saving...');
    },

    saved: function(message) {
        return this.done(message || 'Saved!');
    },

    doing: function(message) {
        return this.notify({
            message: message,
            delay: 0
        });
    },

    done: function(message) {
        return this.notify({
            message: message
        });
    },

    error: function(message) {
        return this.notify({
            message: message || 'Something went wrong... :(',
            type: 'danger'
        });
    },

    notify: function(options) {
        return $.notify({
            message: options.message
        }, {
            type: options.type || 'info',
            delay: options.delay || 5000,
            newest_on_top: true,
            placement: {
                align: 'center'
            }
        });
    }
};

module.exports = {
    notify: notify
};
