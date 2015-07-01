var dialog = {
    confirmInvalidUrl: function(linkName, checkStatus, addFunc) {
        bootbox.dialog({
            message: 'We think "{}" is an invalid link. Are you sure you want to add it?'
                .replace('{}', linkName),
            buttons: {
                danger: {
                    label: 'Add',
                    className: 'btn-warning',
                    callback: function() {
                        addFunc(checkStatus);
                    }
                }
            }
        });
    },

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
    },

    selector: function(title, template, callbacks) {
        bootbox.dialog({
            title: title,
            message: template,
            onEscape: callbacks.cancel,
            buttons: {
                cancel: {
                    label: 'Cancel',
                    className: 'btn-default',
                    callback: callbacks.cancel
                },
                done: {
                    label: 'Done',
                    className: 'btn-primary',
                    callback: callbacks.done
                }
            }
        });
    }
};

module.exports = {
    dialog: dialog
};
