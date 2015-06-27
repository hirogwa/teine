var PhotoListView = Backbone.View.extend({
    events: {
        'click button.delete-photo': 'deletePhoto'
    },

    initialize: function(options) {
        _.bindAll(this, 'render', 'deletePhoto');
        this.template = require('./photo-list-view.html');
        this.delegates = {
            deletePhoto: options.delegates.deletePhoto
        };
    },

    render: function() {
        this.$el.html(this.template({
            photos: this.collection
        }));
        return this;
    },

    deletePhoto: function(e) {
        this.delegates.deletePhoto(
            $(e.currentTarget).data('photo-id'),
            $(e.currentTarget).data('photo-filename')
        );
    }
});

module.exports = {
    PhotoListView: PhotoListView
};
