teine = {};
$(function() {
    require('./css/dashboard.css');

    teine.ShowEditorView =
        require('./js/views/show/show-editor.js').ShowEditorView;
    teine.EpisodeEditorView =
        require('./js/views/episode/episode-editor.js').EpisodeEditorView;
    teine.EpisodeListView =
        require('./js/views/episode/episode-list-view.js').EpisodeListView;
    teine.MediaManagerView =
        require('./js/views/media/media-manager.js').MediaManagerView;
});
