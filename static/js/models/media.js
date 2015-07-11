var utils = require('../utils.js');

var Media = Backbone.Model.extend({
    url: '/media',

    idAttribute: 'media_id',

    equals: function(another) {
        return another ?
            another.get('media_id') === this.get('media_id') : false;
    },

    formattedSize: function() {
        return '{} MB'.replace('{}', (this.get('size') / 1000000).toFixed(2));
    },

    formattedDatetime: function() {
        return utils.formatDatetime(new Date(this.get('datetime')));
    },

    parse: function(input) {
        return {
            media_id: input.media_id,
            name: input.name,
            size: input.size,
            content_type: input.content_type,
            status: input.status,
            datetime: input.datetime,
            episode: input.episode
        };
    }
});

Media.upload = function(file) {
    var media = new Media();
    return utils.uploadFile(media.url, file).then(function(result) {
        if (result.result === 'success') {
            media.parse(result.media);
            return Promise.resolve(media);
        } else {
            return Promise.reject();
        }
    }, function(reason) {
        return Promise.reject(reason);
    });
};

Media.destroy = function(media_id) {
    return new Promise(function(resolve, reject) {
        new Media({media_id: media_id}).destroy({
            data: $.param({
                media_id: media_id
            }),
            success: function(model, resp, options) {
                resolve();
            },
            error: function(model, resp, options) {
                reject();
            }
        });
    });
};

var MediaCollection = Backbone.Collection.extend({
    model: Media,

    url: '/media-list',

    selectedMedia: function() {
        return this.find(function(m) {
            return m.get('selector-selected');
        });
    }
});

MediaCollection.loadUsed = function() {
    return new Promise(function(resolve, reject) {
        new MediaCollection().fetch({
            data: $.param({
                filter: 'used'
            }),
            success: function(collection, resp, options) {
                resolve(collection);
            },
            error: function(collection, resp, options) {
                reject();
            }
        });
    });
};

MediaCollection.loadUnused = function() {
    return new Promise(function(resolve, reject) {
        new MediaCollection().fetch({
            data: $.param({
                filter: 'unused'
            }),
            success: function(collection, resp, options) {
                resolve(collection);
            },
            error: function(collection, resp, options) {
                reject();
            }
        });
    });
};

module.exports = {
    Media: Media,
    MediaCollection: MediaCollection
};
