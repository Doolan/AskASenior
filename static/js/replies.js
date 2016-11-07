$(document).ready(function () {
    formConfig();
    modalConfig();
});

var submitNewReply = function (fields) {
    console.log(fields);
};

var formConfig = function () {
    $('#newReplyModalForm')
        .form({
            fields: {
                body: {
                    identifier: 'text',
                    rules: [
                        {
                            type: 'empty',
                            prompt: 'Please enter some text for a body'
                        }
                    ]
                }
            },
            onSuccess: function (event, fields) {
                submitNewReply(fields);
            },
            onFailure: function (formErrors, fields) {
                return;
            },
            keyboardShortcuts: false
        });
};

var modalConfig = function () {
    $('#newReplyModal').modal({
        closable: false,
        onDeny: function () {
            return true;
        },
        onApprove: function () {
            $('#newReplyModalForm').form('validate form');
            return $('#newReplyModalForm').form('is valid');
        }
    });
};

var launchModal = function () {
    $('#newReplyModal').modal('show');
    $('#newReplyModalForm').form('reset');
    $('#newReplyModalForm .error.message').empty();
};