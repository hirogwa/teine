teine = {};
bootbox = require('bootbox');
$(function() {
    require('./css/dashboard.css');
    require('./js/esnext.js');

    teine.ProfileEditorView =
        require('./js/views/profile/profile-editor.js').ProfileEditorView;
    teine.ShowEditorView =
        require('./js/views/show/show-editor.js').ShowEditorView;
    teine.EpisodeEditorView =
        require('./js/views/episode/episode-editor.js').EpisodeEditorView;
    teine.EpisodeListView =
        require('./js/views/episode/episode-list-view.js').EpisodeListView;
    teine.MediaManagerView =
        require('./js/views/media/media-manager.js').MediaManagerView;
    teine.PhotoManagerView =
        require('./js/views/photo/photo-manager.js').PhotoManagerView;
});
