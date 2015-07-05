var utils = require('../utils.js');

var Photo = Backbone.Model.extend({
    url: '/photo',

    equals: function(another) {
        return another ?
            another.get('photo_id') === this.get('photo_id') : false;
    },

    formattedDatetime: function() {
        return utils.formatDatetime(new Date(this.get('datetime')));
    }
});

Photo.upload = function(file) {
    return utils.uploadFile('/upload-photo', file).then(function(result) {
        if (result.result === 'success') {
            return Promise.resolve(new Photo(result.photo));
        } else {
            return Promise.reject();
        }
    }, function(reason) {
        return Promise.reject();
    });
};

Photo.destroy = function(photo_id) {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '/photo?{}'.replace('{}', $.param({
                photo_id: photo_id
            })),
            method: 'DELETE',
            success: function(data) {
                if (data.result === 'success') {
                    resolve();
                } else {
                    reject(data);
                }
            },
            error: function(data) {
                reject(data);
            }
        });
    });
};

var PhotoCollection = Backbone.Collection.extend({
    model: Photo
});

PhotoCollection.load = function() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '/load-photos',
            success: function(data) {
                if (data.result === 'success') {
                    var c = new PhotoCollection();
                    c.reset(data.photos.map(function(p) {
                        return new Photo(p);
                    }));
                    resolve(c);
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

module.exports = {
    Photo: Photo,
    PhotoCollection: PhotoCollection
};
