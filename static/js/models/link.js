var Link = Backbone.Model;

var Links  = Backbone.Collection.extend({
    model: Link,

    addLink: function(params) {
        this.add(new Link({
            url: params.url,
            title: params.title
        }));
    }
});

module.exports = {
    Link: Link,
    Links: Links
};
