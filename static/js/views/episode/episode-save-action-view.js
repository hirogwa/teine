var episodeSaveActionViewTemplate =
    require('./episode-save-action-view.html');
var EpisodeSaveActionView = Backbone.View.extend({
    events: {
        'change input#episode-save-option-draft': 'selectDraftOption',
        'change input#episode-save-option-schedule': 'selectScheduleOption',
        'change input#episode-save-option-publish': 'selectPublishOption',
        'change input#scheduled-date': 'changeScheduledDate',
        'click button#save-draft': 'saveDraft',
        'click button#schedule': 'schedule',
        'click button#publish': 'publish'
    },

    initialize: function(options) {
        _.bindAll(this, 'render', 'saveDraft', 'schedule', 'publish',
                  'changeScheduledDate',
                  'selectDraftOption',
                  'selectScheduleOption',
                  'selectPublishOption');
        this.template = episodeSaveActionViewTemplate;
        if (options && options.delegates) {
            this.delegates = {
                saveDraft: options.delegates.saveDraft || function() {},
                schedule: options.delegates.schedule || function() {},
                publish: options.delegates.publish || function() {}
            };
        }
        if (options && options.status) {
            console.log(options);
            this.savedAs = options.status.saved_as;
            this.scheduleDate = options.status.schedule_date;
        }
        this.savedAs = this.savedAs || 'draft';
        if (!this.scheduleDate) {
            var today = new Date();
            this.scheduleDate = 'yyyy-mm-dd'
                .replace('yyyy', today.getFullYear())
                .replace('mm', this.formatTwoDigits(today.getMonth() + 1))
                .replace('dd', this.formatTwoDigits(today.getDate()));
        }
        this.render();
    },

    formatTwoDigits: function(n) {
        return n < 10 ? '0{}'.replace('{}', n) : n;
    },

    render: function() {
        this.$el.html(this.template({
            draftSelected: this.savedAs === 'draft',
            scheduleSelected: this.savedAs === 'scheduled',
            publishSelected: this.savedAs === 'published',
            scheduleDate: this.scheduleDate
        }));
        return this;
    },

    selectDraftOption: function(e) {
        this.savedAs = 'draft';
        return this.render();
    },

    selectScheduleOption: function(e) {
        this.savedAs = 'scheduled';
        return this.render();
    },

    selectPublishOption: function(e) {
        this.savedAs = 'published';
        return this.render();
    },

    changeScheduledDate: function(e) {
        var dateValue = e.currentTarget.value;
        if (!dateValue) {
            e.currentTarget.valueAsDate = new Date();
        }
        this.scheduleDate = e.currentTarget.value;
    },

    saveDraft: function(e) {
        this.delegates.saveDraft(e);
        return this;
    },

    schedule: function(e) {
        this.delegates.schedule(e, {
            scheduled_date: $('#scheduled-date').val()
        });
        return this;
    },

    publish: function(e) {
        this.delegates.publish(e);
        return this;
    }
});

module.exports = {
    EpisodeSaveActionView: EpisodeSaveActionView
};
