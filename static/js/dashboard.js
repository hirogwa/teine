teine = {};
$(function() {
    teine.ShowEditorView =
        require('./views/show/show-editor.js').ShowEditorView;
    teine.EpisodeEditorView =
        require('./views/episode/episode-editor.js').EpisodeEditorView;
    teine.EpisodeListView =
        require('./views/episode/episode-list-view.js').EpisodeListView;
    teine.MediaManagerView =
        require('./views/media/media-manager.js').MediaManagerView;
});
