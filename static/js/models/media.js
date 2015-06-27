var utils = require('../utils.js');

var Media = Backbone.Model.extend({
    upload: function() {
        return utils.uploadFile('/upload-media', this.get('file'));
    },

    formattedSize: function() {
        return '{} MB'.replace('{}', (this.get('size') / 1000000).toFixed(2));
    },

    formattedDatetime: function() {
        return utils.formatDatetime(new Date(this.get('datetime')));
    }
});

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
                console.log(data);
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
        contentType: input.content_type,
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
