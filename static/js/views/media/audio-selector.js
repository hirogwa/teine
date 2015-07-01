var models = {
    MediaCollection: require('../../models/media.js').MediaCollection
};

var dialog = require('../utils/dialog.js').dialog;

var AudioSelector = Backbone.View.extend({
    events: {
        'click tr.selectable-audio': 'selectAudio'
    },

    initialize: function(args) {
        var options = args || {};
        this.additionalAudio = options.additionalAudio;
        _.bindAll(this, 'render', 'showDialog');
        this.template = require('./audio-selector.html');
        this.refreshCollection();
    },

    render: function() {
        this.$el.html(this.template({
            collection: this.collection
        }));
        return this;
    },

    refreshCollection: function() {
        var self = this;
        this.loadCollection = models.MediaCollection.loadUnused()
            .then(function(result) {
                self.collection = result;
                if (self.additionalAudio) {
                    self.collection.add(self.additionalAudio);
                }
                self.render();
                return Promise.resolve();
            }, function(reason) {
                return Promise.reject(reason);
            });
    },

    selectAudio: function(e) {
        var self = this;
        var selectedId = $(e.currentTarget).data('media-id');
        var selectIt = function() {
            self.selectedAudio = self.collection.find(function(m) {
                return m.get('media_id') === selectedId;
            });
            self.selectedAudio.selected = true;
        };

        if (this.selectedAudio) {
            this.selectedAudio.selected = false;
            if (this.selectedAudio.get('media_id') === selectedId) {
                this.selectedAudio = undefined;
            } else {
                selectIt();
            }
        } else {
            selectIt();
        }
        this.render();
    },

    changeInputFile: function() {
    },

    showDialog: function() {
        var self = this;
        return this.loadCollection.then(function(result) {
            return new Promise(function(resolve, reject) {
                dialog.selector('Select audio', self.$el, {
                    cancel: function() {
                        resolve();
                    },
                    done: function() {
                        resolve(self.selectedAudio);
                    }
                });
            });
        }, function(reason) {
            return Promise.reject(reason);
        });
    }
});

module.exports = {
    AudioSelector: AudioSelector
};
