require('bootstrapNotify');

var notify = {
    uploading: function(entityName, options) {
        return this.doing('Uploading {}...'.replace('{}', entityName), options);
    },

    uploaded: function(entityName, options) {
        return this.done('{} uploaded!'.replace('{}', entityName), options);
    },

    deleting: function(entityName) {
        return this.doing('Deleting {}...'.replace('{}', entityName));
    },

    deleted: function(entityName) {
        return this.done('{} deleted!'.replace('{}', entityName));
    },

    saving: function(message) {
        return this.doing(message || 'Saving...');
    },

    saved: function(message) {
        return this.done(message || 'Saved!');
    },

    doing: function(message, args) {
        var options = args || {};
        options.message = message || options.message;
        options.delay = options.delay || 0;
        return this.notify(options);
    },

    done: function(message, args) {
        var options = args || {};
        options.message = message || options.message;
        options.delay = options.delay || 0;
        return this.notify(options);
    },

    warn: function(message, args) {
        var options = args || {};
        options.message = message;
        options.type = 'warning';
        return this.notify(options);
    },

    error: function(message, args) {
        var options = args || {};
        options.message =
            message || options.message || 'Something went wrong... :(';
        options.type = 'danger';
        return this.notify(options);
    },

    notify: function(options) {
        return $.notify({
            message: options.message
        }, {
            type: options.type || 'info',
            delay: options.delay || 5000,
            newest_on_top: true,
            element: options.element || 'body',
            placement: {
                align: 'center'
            }
        });
    }
};

module.exports = {
    notify: notify
};
