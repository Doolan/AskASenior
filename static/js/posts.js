$(document).ready(function () {
    formConfig();
    modalConfig();
});

var submitNewPost = function (fields) {
//    fields.is_anonymous = fields.is_anonymous == 'on';
    if(fields.is_anonymous == 'on') {
    	fields.is_anonymous = 'true';
    } else {
    	fields.is_anonymous = 'false';
    }
    console.log(fields);
    
    $.post( "/post", fields ).done(function( json ) {
//	    console.log("Response JSON: " + JSON.stringify(json));
	}).fail(function(jqxhr, textStatus, error) {
	    console.log("POST Request Failed: " + textStatus + ", " + error);
	});
};

var formConfig = function () {
    $('#postModalForm')
        .form({
            fields: {
                title: {
                    identifier: 'title',
                    rules: [
                        {
                            type: 'empty',
                            prompt: 'Please enter a title'
                        }
                    ]
                },
                body: {
                    identifier: 'body',
                    rules: [
                        {
                            type: 'empty',
                            prompt: 'Please enter some text for a body'
                        }
                    ]
                },
                type: {
                    identifier: 'type',
                    rules: [
                        {
                            type: 'empty',
                            prompt: 'Please select a type'
                        }
                    ]
                },
                cat: {
                    identifier: 'category',
                    rules: [
                        {
                            type: 'empty',
                            prompt: 'Please select a category'
                        }
                    ]
                },
            },
            onSuccess: function (event, fields) {
                submitNewPost(fields);
            },
            onFailure: function (formErrors, fields) {
                return;
            },
            keyboardShortcuts: false
        });
};

var modalConfig = function () {
    $('#newPostModal').modal({
        closable: false,
        onDeny: function () {
            return true;
        },
        onApprove: function () {
            $('#postModalForm').form('validate form');
            return $('#postModalForm').form('is valid');
        }
    });
};

var launchModal = function () {
    $('#newPostModal').modal('show');
    $('#postModalForm').form('reset');
    $('#newPostModal .error.message').empty();
};