var mediaSelectorViewTemplate = require('./media-selector-view.html');
var MediaSelectorView = Backbone.View.extend({
    events: {
        'click button.media-selector-select': 'selectMedia',
        'click button.media-selector-deselect': 'deselectMedia'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'selectMedia');
        this.template = mediaSelectorViewTemplate;
    },

    render: function() {
        this.$el.html(this.template({
            collection: this.collection
        }));
        return this;
    },

    selectMedia: function(e) {
        var targetId = $(e.currentTarget).data('media-id');
        this.collection.forEach(function(m) {
            m.set({
                'selector-selected': m.get('media_id') === targetId
            });
        });
        return this.render();
    },

    deselectMedia: function(e) {
        this.collection.forEach(function(m) {
            m.set({
                'selector-selected': false
            });
        });
        return this.render();
    }
});

module.exports = {
    MediaSelectorView: MediaSelectorView
};