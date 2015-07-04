var models = {
    Media: require('../../models/media.js').Media,
    MediaCollection: require('../../models/media.js').MediaCollection,
    Episode: require('../../models/episode.js').Episode
};

var dialog = require('../utils/dialog.js').dialog;

var notify = require('../utils/notification.js').notify;

var AudioSelector = Backbone.View.extend({
    events: {
        'click tr.selectable-audio': 'onAudioSelect',
        'change #audio-selector-file-input': 'changeInputFile'
    },

    initialize: function(args) {
        _.bindAll(this, 'render', 'showDialog', 'changeInputFile',
                  'onAudioSelect', 'selectAudio');
        this.template = require('./audio-selector.html');

        var options = args || {};
        this.originallySelected = options.selectedAudio;
        this.selectedAudio = options.selectedAudio;
        this.targetEpisode = options.targetEpisode;
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
            .then(function(audioCollection) {
                if (self.targetEpisode) {
                    return models.Episode.load(self.targetEpisode.get('episode_id'))
                        .then(function(reservedAudio) {
                            if (!audioCollection.find(function(a) {
                                return a.equals(reservedAudio);
                            })) {
                                audioCollection.add(reservedAudio.media);
                            }
                            return Promise.resolve(audioCollection);
                        });
                } else {
                    return Promise.resolve(result);
                }
            })
            .then(function(audioCollection) {
                if (self.selectedAudio) {
                    self.selectedAudio = audioCollection.find(function(a) {
                        return a.equals(self.selectedAudio);
                    });
                    self.selectedAudio.selected = true;
                }
                self.collection = audioCollection;
                self.render();
                return Promise.resolve();
            }, function(reason) {
                return Promise.reject(reason);
            });
        return this.loadCollection;
    },

    onAudioSelect: function(e) {
        this.selectAudio($(e.currentTarget).data('media-id'));
    },

    selectAudio: function(mediaId) {
        var self = this;
        var selectIt = function() {
            self.selectedAudio = self.collection.find(function(m) {
                return m.get('media_id') === mediaId;
            });
            self.selectedAudio.selected = true;
        };

        if (this.selectedAudio) {
            this.selectedAudio.selected = false;
            if (this.selectedAudio.get('media_id') === mediaId) {
                this.selectedAudio = undefined;
            } else {
                selectIt();
            }
        } else {
            selectIt();
        }
        this.render();
    },

    changeInputFile: function(e) {
        var self = this;
        var file = e.currentTarget.files[0];
        $(e.currentTarget).val('');

        var notifyOptions = {
            element: 'audio-selector-notify'
        };
        var uploadedAudio;
        var notifyUploading = notify.uploading(file.name, notifyOptions);
        models.Media.upload(file).then(function(result) {
            notifyUploading.close();
            notify.uploaded(file.name, notifyOptions);
            uploadedAudio = result;
            return self.refreshCollection();
        }).then(function(result) {
            self.selectAudio(uploadedAudio.get('media_id'));
        }, function(reason) {
            notify.error(notifyOptions);
        });
        return this;
    },

    showDialog: function() {
        var self = this;
        return this.loadCollection.then(function(result) {
            return new Promise(function(resolve, reject) {
                dialog.selector('Select audio', self.$el, {
                    cancel: function() {
                        resolve(self.originallySelected);
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
