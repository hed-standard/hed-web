

$(function () {
    prepareForm();
})


$('#process_actions').change(function(){
    setOptions();
    setEventsTable('#events_file')
});


/**
 * Events file handler function. Checks if the file uploaded has a valid spreadsheet extension.
 */
$('#events_file').on('change', function () {
    let eventsPath = $('#events_file').val();
    if (cancelWasPressedInChromeFileUpload(eventsPath) || !fileHasValidExtension(eventsPath, TEXT_FILE_EXTENSIONS)) {
        clearForm();
        flashMessageOnScreen('Please upload a tsv file (.tsv, .txt)', 'error', 'events_flash');
        return;
    }
    setEventsTable('#events_file')
    updateFileLabel(eventsPath, '#events_display_name');
});

/**
 * Submits the form if there is an events file and an available hed schema
 */
$('#events_submit').on('click', function () {
    if (fileIsSpecified('#events_file', 'events_flash', 'Events file is not specified.')
        && schemaSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});


/**
 * Clears the fields in the form.
 */
function clearForm() {
    $('#events_form')[0].reset();
    $('#events_display_name').text('');
    $("#validate").prop('checked', true);
    setOptions();
    clearFlashMessages();
    hideColumnInfo("show_columns");
    hideColumnInfo("show_events");
    hideOtherSchemaVersionFileUpload();
}

/**
 * Clear the flash messages that aren't related to the form submission.
 */
function clearFlashMessages() {
    clearColumnInfoFlashMessages();
    clearSchemaSelectFlashMessages();
    clearJsonInputFlashMessages();
    flashMessageOnScreen('', 'success', 'events_flash');
    flashMessageOnScreen('', 'success', 'events_submit_flash');
}


/**
 * Prepare the validation form after the page is ready. The form will be reset to handle page refresh and
 * components will be hidden and populated.
 */
function prepareForm() {
    clearForm();
    getSchemaVersions()
    hideOtherSchemaVersionFileUpload();
}

/**
 * Sets the column table for this event file
 * @param {string} event_tag  - jquery tag pointing to the event file.
 */
function setEventsTable(event_tag) {
    clearFlashMessages();
    removeColumnInfo("show_columns");
    removeColumnInfo("show_events")
    let events = $(event_tag);
    let eventsFile = events[0].files[0];
    if ($("#generate_sidecar").is(":checked")) {
        setColumnsInfo(eventsFile, 'events_flash', undefined, true,  "show_events")
    } else {
        setColumnsInfo(eventsFile, 'events_flash', undefined, true,  "show_columns")
    }
}

/**
 * Set the options for the events depending on the action
 */
function setOptions() {
    if ($("#validate").is(":checked")) {
        hideOption("expand_defs");
        showOption("check_for_warnings");
        $("#json_input_section").show();
        $("#schema_pulldown_section").show();
        $("#options_section").show();
    } else if ($("#assemble").is(":checked")) {
        hideOption("check_for_warnings");
        showOption("expand_defs");
        $("#json_input_section").show();
        $("#schema_pulldown_section").show();
        $("#options_section").show();
    } else if ($("#generate_sidecar").is(":checked")) {
        hideOption("check_for_warnings");
        hideOption("expand_defs");
        $("#json_input_section").hide();
        $("#schema_pulldown_section").hide();
        $("#options_section").hide();
    }
}

/**
 * Submit the form and return the validation results. If there are issues then they are returned in an attachment
 * file.
 */
function submitForm() {
    let eventsForm = document.getElementById("events_form");
    let formData = new FormData(eventsForm);
    let prefix = 'issues';
    let eventsFile = $('#events_file')[0].files[0].name;
    let display_name = convertToResultsName(eventsFile, prefix)
    clearFlashMessages();
    flashMessageOnScreen('Event file is being processed ...', 'success',
        'events_submit_flash')
    $.ajax({
            type: 'POST',
            url: "{{url_for('route_blueprint.events_results')}}",
            data: formData,
            contentType: false,
            processData: false,
            dataType: 'text',
            success: function (download, status, xhr) {
                getResponseSuccess(download, xhr, display_name, 'events_submit_flash')
            },
            error: function (xhr, status, errorThrown) {
                getResponseFailure(xhr, status, errorThrown, display_name, 'events_submit_flash')
            }
        }
    )
}