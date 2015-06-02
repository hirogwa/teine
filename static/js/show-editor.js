var views = require('./views.js');
var models = require('./models.js');

var showEditorTemplate = require('./templates/show-editor.html');
var ShowEditorView = Backbone.View.extend({
    el: $('#show-editor'),

    events: {
        'click button#save-show': 'saveShow'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'saveShow');
        this.show = new models.Show();
        this.peopleView = new views.PersonalityListView({
            collection: this.show.get('regularHosts')
        });

        this.template = showEditorTemplate;
        this.render();
    },

    render: function() {
        console.log('rendering show editor');
        this.$el.html(this.template({
        }));
        this.$('#show-regular-hosts').append(this.peopleView.render().el);

        this.peopleView.postRender();

        return this;
    },

    saveShow: function() {
        this.show.set({
            title: $('#show-title').val(),
            tagline: $('#show-tagline').val(),
            description: $('#show-description').val()
        });
        this.show.save();
    }
});

new ShowEditorView();
