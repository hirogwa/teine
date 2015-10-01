var Link = Backbone.Model;

var Links  = Backbone.Collection.extend({
    model: Link,

    addLink: function(params) {
        this.add(new Link({
            url: params.url,
            title: params.title
        }));
    },

    moveUp: function(link) {
        var index = this.indexOf(link);
        if (index < 1) {
            return this;
        }
        this.remove(link);
        this.add(link, { at: index - 1 });
        return this;
    },

    moveDown: function(link) {
        var index = this.indexOf(link);
        if (index === -1 || index === this.length - 1) {
            return this;
        }
        this.remove(link);
        this.add(link, { at: index + 1 });
        return this;
    }
});

module.exports = {
    Link: Link,
    Links: Links
};
