/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	$(function() {
	    __webpack_require__(1);
	});


/***/ },
/* 1 */
/***/ function(module, exports, __webpack_require__) {

	var models = __webpack_require__(3);
	var views = __webpack_require__(4);
	var episodeEditorTemplate = __webpack_require__(2);

	var EpisodeEditorView = Backbone.View.extend({
	    el: $('#episode-editor'),

	    events: {
	        'change input#episode-title': 'changeTitle',
	        'change input#episode-summary': 'changeSummary',
	        'change input#episode-description': 'changeDescription',
	        'change input#episode-audio': 'changeAudio',
	        'change input#schedule-datetime': 'changeScheduleDatetime',

	        'click button#upload-episode-audio': 'uploadEpisodeAudio',

	        'click button#add-personality': 'addPersonality',
	        'click button#publish': 'publish',
	        'click button#save-draft': 'saveDraft',
	        'click button#schedule': 'schedule'
	    },

	    initialize: function() {
	        _.bindAll(this, 'render',
	                  'changeTitle', 'changeSummary', 'changeDescription',
	                  'changeScheduleDatetime',
	                  'addPersonality',
	                  'publish', 'saveDraft', 'schedule');

	        this.episode = new models.Episode();
	        this.peopleView = new views.PersonalityListView({
	            collection: this.episode.get('people')
	        });
	        this.linkListView = new views.LinkListView({
	            collection: this.episode.get('links')
	        });

	        this.template = episodeEditorTemplate;
	        this.render();
	        console.log('init');
	    },

	    render: function() {
	        this.$el.html(this.template({
	            people: this.episode.get('people')
	        }));
	        this.$('#episode-personality-list').append(this.peopleView.render().el);
	        this.$('#episode-external-links').append(this.linkListView.render().el);

	        this.peopleView.postRender();

	        return this;
	    },

	    uploadEpisodeAudio: function(e) {
	        var file = $('#episode-audio')[0].files[0];
	        if (file) {
	            var data = new FormData();
	            data.append('file', file);

	            var media = new models.Media({
	                data: data
	            });

	            media.upload();
	        }
	        console.log(file);
	    },

	    changeTitle: function(e) {
	        this.episode.set({
	            title: e.currentTarget.value
	        });
	    },

	    changeSummary: function(e) {
	        this.episode.set({
	            summary: e.currentTarget.value
	        });
	    },

	    changeDescription: function(e) {
	        this.episode.set({
	            description: e.currentTarget.value
	        });
	    },

	    changeAudio: function(e) {
	        console.log(e);
	    },

	    changeScheduleDatetime: function(e) {
	        this.episode.set({
	            scheduledAt: e.currentTarget.value
	        });
	    },

	    addPersonality: function(e) {
	        this.episode.get('people').add(new models.Personality({
	            twitter: $('#new-personality-twitter').val()
	        }));
	    },

	    publish: function(e) {
	        this.episode.publish();
	    },

	    saveDraft: function(e) {
	        this.episode.saveDraft();
	    },

	    schedule: function(e) {
	        this.episode.schedule();
	    }
	});

	new EpisodeEditorView();


/***/ },
/* 2 */
/***/ function(module, exports, __webpack_require__) {

	module.exports = function(obj){
	var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
	with(obj||{}){
	__p+='<input id="episode-title" placeholder="title">\n<input id="episode-summary" placeholder="summary">\n<input id="episode-description" placeholder="description">\n\n<h4>Audio</h4>\n<input id="episode-audio" type="file">\n<button id="upload-episode-audio" class="btn btn-sm">Add media</button>\n\n<h4>Links</h4>\n<div id="episode-external-links">\n</div>\n\n<h4>People</h4>\n<div id="episode-personality-list">\n</div>\n\n<hr>\n<button class="btn" id="publish">Publish</button>\n<button class="btn" id="save-draft">Save draft</button>\n\n<input id="schedule-datetime" type="date">\n<button class="btn" id="schedule">Schedule</button>\n';
	}
	return __p;
	};

/***/ },
/* 3 */
/***/ function(module, exports, __webpack_require__) {

	var Media = Backbone.Model.extend({
	    upload: function() {
	        var self = this;
	        $.ajax({
	            url: '/media',
	            data: self.get('data'),
	            cache: false,
	            processData: false,
	            contentType: false,
	            method: 'POST',
	            success: function(data) {
	                console.log(data);
	            },
	            error: function(data) {
	                console.log(data);
	            }
	        });
	    }
	});

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

	var Personality = Backbone.Model;

	var People = Backbone.Collection.extend({
	    model: Personality,

	    addPersonalityFromTwitter: function(params) {
	        this.add(new Personality({
	            source: 'twitter',
	            id: params.screen_name,
	            name: params.name,
	            description: params.description,
	            profile_image_url: params.profile_image_url
	                .replace('_normal', '_400x400')
	        }));
	    }
	});

	var Episode = Backbone.Model.extend({
	    url: '/episode',

	    defaults: {
	        links: new Links(),
	        people: new People()
	    },

	    saveType: function(input) {
	        this.set({
	            savedAs: input
	        });
	    },

	    publish: function() {
	        this.saveType('published');
	        this.save();
	    },

	    saveDraft: function() {
	        this.saveType('draft');
	        this.save();
	    },

	    schedule: function() {
	        this.saveType('scheduled');
	        this.save();
	    }
	});

	module.exports = {
	    Media: Media,
	    Link: Link,
	    Links: Links,
	    Personality: Personality,
	    People: People,
	    Episode: Episode
	};


/***/ },
/* 4 */
/***/ function(module, exports, __webpack_require__) {

	var linkViewTemplate = __webpack_require__(7);
	var LinkView = Backbone.View.extend({
	    events: {
	        'click button#remove-link': 'removeLink'
	    },

	    initialize: function() {
	        _.bindAll(this, 'render');
	        this.template = linkViewTemplate;
	    },

	    render: function() {
	        this.$el.html(this.template({
	            url: this.model.get('url'),
	            title: this.model.get('title')
	        }));
	        return this;
	    },

	    removeLink: function(e) {
	        this.model.collection.remove(this.model);
	        return this;
	    }
	});

	var linkListViewTemplate = __webpack_require__(8);
	var LinkListView = Backbone.View.extend({
	    events: {
	        'click button#add-link': 'addLink',
	    },

	    initialize: function() {
	        _.bindAll(this, 'render', 'renderAdd', 'addLink');
	        this.template = linkListViewTemplate;

	        this.collection.on('add', this.renderAdd);
	        this.collection.on('remove', this.render);
	    },

	    render: function() {
	        this.$el.html(this.template());
	        this.collection.models.forEach(function(l) {
	            this.renderAdd(l);
	        }, this);
	        return this;
	    },

	    renderAdd: function(l) {
	        this.$('#external-link-list').append(new LinkView({
	            model: l
	        }).render().el);
	        return this;
	    },

	    addLink: function(e) {
	        this.collection.addLink({
	            title: $('#new-link-title').val(),
	            url: $('#new-link-url').val()
	        });
	        return this;
	    }
	});

	var personalityViewTemplate = __webpack_require__(5);
	var PersonalityView = Backbone.View.extend({
	    events: {
	        'click button.remove-personality': 'removePersonality'
	    },

	    initialize: function() {
	        _.bindAll(this, 'render', 'removePersonality');
	        this.template = personalityViewTemplate;
	    },

	    render: function() {
	        this.$el.html(this.template({
	            id: this.model.get('id'),
	            name: this.model.get('name'),
	            description: this.model.get('description'),
	            profile_image_url: this.model.get('profile_image_url')
	        }));
	        return this;
	    },

	    removePersonality: function(e) {
	        this.model.collection.remove(this.model);
	        return this;
	    }
	});

	var personalityListViewTemplate = __webpack_require__(6);
	var PersonalityListView = Backbone.View.extend({
	    initialize: function() {
	        _.bindAll(this, 'render', 'renderAdd', 'postRender', 'renderFull',
	                  'formatTwitterUserResult', 'formatTwitterUserSelection');
	        this.template = personalityListViewTemplate;
	        this.collection.on('add', this.renderAdd);
	        this.collection.on('remove', this.renderFull);
	        this.collection.on('reset', this.renderFull);
	    },

	    renderFull: function() {
	        return this.render().postRender();
	    },

	    render: function() {
	        this.$el.html(this.template());
	        this.collection.forEach(function(p) {
	            this.renderAdd(p);
	        }, this);

	        return this;
	    },

	    renderAdd: function(p) {
	        this.$('#personality-list').append(new PersonalityView({
	            model: p
	        }).render().el);
	        return this;
	    },

	    postRender: function() {
	        var self = this;
	        var twitterUserSelect = '#select-twitter-user';
	        $(twitterUserSelect).select2({
	            ajax: {
	                url: '/twitter-user-search',
	                dataType: 'json',
	                delay: 500,
	                data: function(params) {
	                    return {
	                        q: params.term
	                    };
	                },
	                processResults: function(data, page) {
	                    return {
	                        results: data
	                    };
	                }
	            },
	            minimumInputLength: 2,
	            escapeMarkup: function(markup) {
	                return markup;
	            },
	            templateResult: function(result) {
	                return self.formatTwitterUserResult(result);
	            },
	            templateSelection: function(item) {
	                return self.formatTwitterUserSelection(item);
	            }
	        });

	        $(twitterUserSelect).on('change', function(e) {
	            var item = $(twitterUserSelect).select2('data')[0];
	            self.collection.addPersonalityFromTwitter(item);
	        });

	        return this;
	    },

	    formatTwitterUserResult: function(result) {
	        if (result.loading) {
	            return result.text;
	        }
	        return '<div>' +
	            '<img src="' + result.profile_image_url + '"/>' +
	            '<span>' + result.screen_name + ' ' + result.name + '</span>' +
	            '</div>';
	    },

	    formatTwitterUserSelection: function(item) {
	        //return 'Type in name to add...';
	        return '';
	    }
	});

	module.exports = {
	    LinkListView: LinkListView,
	    PersonalityView: PersonalityView,
	    PersonalityListView: PersonalityListView
	};


/***/ },
/* 5 */
/***/ function(module, exports, __webpack_require__) {

	module.exports = function(obj){
	var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
	with(obj||{}){
	__p+='<div>\n  <button class="btn btn-sm remove-personality">\n    <i class="fa fa-times"></i>\n  </button>\n  '+
	((__t=( id ))==null?'':__t)+
	' <br>\n  '+
	((__t=( name ))==null?'':__t)+
	' <br>\n  '+
	((__t=( description ))==null?'':__t)+
	' <br>\n  <img src="'+
	((__t=( profile_image_url ))==null?'':__t)+
	'" alt="profile image"\n       width="80" height="80"/>\n</div>\n';
	}
	return __p;
	};

/***/ },
/* 6 */
/***/ function(module, exports, __webpack_require__) {

	module.exports = function(obj){
	var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
	with(obj||{}){
	__p+='<select id="select-twitter-user">\n  <option selected="selected"></option>\n</select>\n<div id="personality-list">\n</div>\n';
	}
	return __p;
	};

/***/ },
/* 7 */
/***/ function(module, exports, __webpack_require__) {

	module.exports = function(obj){
	var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
	with(obj||{}){
	__p+=''+
	((__t=( url ))==null?'':__t)+
	'\n'+
	((__t=( title ))==null?'':__t)+
	'\n<button id="remove-link" class="btn btn-sm"><i class="fa fa-times"></i></button>\n';
	}
	return __p;
	};

/***/ },
/* 8 */
/***/ function(module, exports, __webpack_require__) {

	module.exports = function(obj){
	var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
	with(obj||{}){
	__p+='<input id="new-link-url" placeholder="url">\n<input id="new-link-title" placeholder="title">\n<button class="btn btn-sm" id="add-link"><i class="fa fa-plus"></i></button>\n<div id="external-link-list">\n</div>\n';
	}
	return __p;
	};

/***/ }
/******/ ]);