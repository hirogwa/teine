var utils = require('../utils.js');

var Media = Backbone.Model.extend({
    equals: function(another) {
        return another ?
            another.get('media_id') === this.get('media_id') : false;
    },

    formattedSize: function() {
        return '{} MB'.replace('{}', (this.get('size') / 1000000).toFixed(2));
    },

    formattedDatetime: function() {
        return utils.formatDatetime(new Date(this.get('datetime')));
    }
});

Media.upload = function(file) {
    return utils.uploadFile('/upload-media', file).then(function(result) {
        if (result.result === 'success') {
            return Promise.resolve(Media.existingData(result.media));
        } else {
            return Promise.reject();
        }
    }, function(reason) {
        return Promise.reject(reason);
    });
};

Media.destroy = function(media_id) {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '/delete-media',
            data: {
                media_id: media_id
            },
            dataType: 'json',
            method: 'POST',
            success: function(data) {
                if (data.result === 'success') {
                    resolve();
                } else {
                    reject();
                }
            },
            error: function(data) {
                reject(data);
            }
        });
    });
};

Media.existingData = function(input) {
    return new Media({
        media_id: input.media_id,
        name: input.name,
        size: input.size,
        content_type: input.content_type,
        status: input.status,
        datetime: input.datetime,
        episode: input.episode
    });
};

var MediaCollection = Backbone.Collection.extend({
    model: Media,

    selectedMedia: function() {
        return this.find(function(m) {
            return m.get('selector-selected');
        });
    }
});

MediaCollection.existingCollection = function(input) {
    var c = new MediaCollection();
    input.forEach(function(m) {
        c.add(Media.existingData(m));
    });
    return c;
};

MediaCollection.loadUsed = function() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '/media-list',
            method: 'GET',
            data: {
                filter: 'used'
            },
            success: function(data) {
                resolve(MediaCollection.existingCollection(data));
            },
            error: function(data) {
                reject(data);
            }
        });
    });
};

MediaCollection.loadUnused = function() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '/media-list',
            method: 'GET',
            data: {
                filter: 'unused'
            },
            success: function(data) {
                resolve(MediaCollection.existingCollection(data));
            },
            error: function(data) {
                reject(data);
            }
        });
    });
};

module.exports = {
    Media: Media,
    MediaCollection: MediaCollection
};
