var utils = require('../utils.js');

var Photo = Backbone.Model.extend({
    url: '/photo',

    idAttribute: 'photo_id',

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
        new Photo({photo_id: photo_id}).destroy({
            data: $.param({
                photo_id: photo_id
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

var PhotoCollection = Backbone.Collection.extend({
    model: Photo,

    url: '/photo-list',

    parse: function(data) {
        return data.photos;
    }
});

PhotoCollection.load = function() {
    return new Promise(function(resolve, reject) {
        new PhotoCollection().fetch({
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
    Photo: Photo,
    PhotoCollection: PhotoCollection
};
