const TEXT_FILE_EXTENSIONS = ['tsv', 'txt'];

$(function () {
    prepareForm();
});


/**
 * Events file handler function. Checks if the file uploaded has a valid spreadsheet extension.
 */
$('#events-file').on('change', function () {
    let events = $('#events-file');
    let eventsPath = events.val();
    clearFormFlashMessages();
    if (cancelWasPressedInChromeFileUpload(eventsPath)) {
        clearForm();
    }
    else if (fileHasValidExtension(eventsPath, TEXT_FILE_EXTENSIONS)) {
        updateFileLabel(eventsPath, '#events-display-name');
        let columnsInfo = getColumnsInfo('events-form', 'events-file');
        let s = '';
    } else {
        clearForm();
        flashMessageOnScreen('Please upload a tsv file (.tsv, .txt)', 'error', 'events-flash');
    }
});

/**
 * Submits the form if there is an events file and an available hed schema
 */
$('#events-validation-submit').on('click', function () {
    if (fileIsSpecified('#events-file', 'events-flash', 'Events file is not specified.')
        && hedSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});


/**
 * Clears the fields in the form.
 */
function clearForm() {
    $('#events-form')[0].reset();
    $('#events-display-name').text('');
    clearFormFlashMessages()
    hideColumnNames();
    hideOtherHEDVersionFileUpload();
}

/**
 * Clear the flash messages that aren't related to the form submission.
 */
function clearFormFlashMessages() {
    flashMessageOnScreen('', 'success', 'events-flash');
    clearJsonFlashMessage()
    flashMessageOnScreen('', 'success', 'hed-select-flash');
    flashMessageOnScreen('', 'success', 'events-validation-submit-flash');
}

/**
 * Prepare the validation form after the page is ready. The form will be reset to handle page refresh and
 * components will be hidden and populated.
 */
function prepareForm() {
    clearForm();
    getHEDVersions()
    hideColumnNames();
    hideOtherHEDVersionFileUpload();
}

/**
 * Submit the form and return the validation results. If there are issues then they are returned in an attachment
 * file.
 */
function submitForm() {
    let eventsForm = document.getElementById("events-form");
    let formData = new FormData(eventsForm);
    let prefix = 'issues';
    let eventsFile = $('#events-file')[0].files[0].name;
    let display_name = convertToResultsName(eventsFile, prefix)
    clearFormFlashMessages();
    flashMessageOnScreen('Worksheet is being validated ...', 'success',
        'events-validation-submit-flash')
    $.ajax({
            type: 'POST',
            url: "{{url_for('route_blueprint.get_events_validation_results')}}",
            data: formData,
            contentType: false,
            processData: false,
            dataType: 'text',
            success: function (download, status, xhr) {
                getResponseSuccess(download, xhr, display_name, 'events-validation-submit-flash')
            },
            error: function (download, status, xhr) {
                getResponseFailure(download, xhr, display_name, 'events-validation-submit-flash')
            }
        }
    )
}