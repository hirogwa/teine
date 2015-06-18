var dialog = {
    confirmDelete: function(entityName, postDelete) {
        bootbox.dialog({
            message: 'Are you sure you want to delete {}?'
                .replace('{}', entityName),
            buttons: {
                cancel: {
                    label: 'Cancel',
                    className: 'btn-default'
                },
                danger: {
                    label: 'Delete',
                    className: 'btn-danger',
                    callback: postDelete
                }
            }
        });
    }
};

module.exports = {
    dialog: dialog
};
