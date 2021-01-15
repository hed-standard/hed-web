const DICTIONARY_FILE_EXTENSIONS = ['json'];

$(function () {
    prepareDictionaryValidationForm();
});

/**
 * Dictionary event handler function. Checks if the file uploaded has a valid dictionary extension.
 */
$('#dictionary-file').on('change',function () {
    let dictionaryPath = $('#dictionary-file').val();
    resetFlashMessages();
    if (cancelWasPressedInChromeFileUpload(dictionaryPath)) {
        resetForm();
    }
    else if (fileHasValidExtension(dictionaryPath, DICTIONARY_FILE_EXTENSIONS)) {
        updateDictionaryFileLabel(dictionaryPath);
    } else {
        resetForm();
        flashMessageOnScreen('Please upload a JSON dictionary (.json)',
            'error', 'dictionary-flash');
    }
});

/**
 * Submits the form if the tag columns textbox is valid.
 */
$('#dictionary-validation-submit').on('click', function () {
    if (dictionaryIsSpecified() && hedSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});

/**
 * Clears the dictionary file label.
 */
function clearDictionaryFileLabel() {
    $('#dictionary-display-name').text('');
}

/**
 * Checks to see if a dictionary has been specified.
 */
function dictionaryIsSpecified() {
    let dictionaryFile = $('#dictionary-file');
    if (dictionaryFile[0].files.length === 0) {
        flashMessageOnScreen('Dictionary is not specified.', 'error',
            'dictionary-flash');
        return false;
    }
    return true;
}


/**
 * Prepare the validation form after the page is ready. The form will be reset to handle page refresh and
 * components will be hidden and populated.
 */
function prepareDictionaryValidationForm() {
    resetForm();
    getHEDVersions()
    hideOtherHEDVersionFileUpload();
}

/**
 * Resets the flash messages that aren't related to the form submission.
 */
function resetFlashMessages() {
    flashMessageOnScreen('', 'success', 'dictionary-flash');
    flashMessageOnScreen('', 'success', 'hed-flash');
    flashMessageOnScreen('', 'success', 'dictionary-validation-submit-flash');
}

/**
 * Resets the fields in the form.
 */
function resetForm() {
    $('#dictionary-form')[0].reset();
    clearDictionaryFileLabel();
    hideOtherHEDVersionFileUpload()
}

/**
 * Submit the form and return the validation results. If there are issues then they are returned in an attachment
 * file.
 */
function submitForm() {
    let dictionaryForm = document.getElementById("dictionary-form");
    let formData = new FormData(dictionaryForm);
    let prefix = 'validation_issues';

    let dictionaryFile = $('#dictionary-file')[0].files[0].name;
    let display_name = convertToResultsName(dictionaryFile, prefix)
    resetFlashMessages();
    flashMessageOnScreen('Dictionary is being validated ...', 'success',
        'dictionary-validation-submit-flash')
    $.ajax({
            type: 'POST',
            url: "{{url_for('route_blueprint.get_dictionary_validation_results')}}",
            data: formData,
            contentType: false,
            processData: false,
            dataType: 'text',
            success: function (downloaded_file) {
                  if (downloaded_file) {
                      flashMessageOnScreen('', 'success',
                          'dictionary-validation-submit-flash');
                      triggerDownloadBlob(downloaded_file, display_name);
                  } else {
                      flashMessageOnScreen('No validation errors found.', 'success',
                          'dictionary-validation-submit-flash');
                  }
            },
            error: function (download_response) {
                console.log(download_response.responseText);
                if (download_response.responseText.length < 100) {
                    flashMessageOnScreen(download_response.responseText, 'error',
                        'dictionary-validation-submit-flash');
                } else {
                    flashMessageOnScreen('Dictionary could not be processed',
                        'error','dictionary-validation-submit-flash');
                }
            }
        }
    )
}


/**
 * Updates the dictionary file label.
 * @param {String} dictionaryPath - The path to the dictionary.
 */
function updateDictionaryFileLabel(dictionaryPath) {
    let dictionaryFilename = dictionaryPath.split('\\').pop();
    $('#dictionary-display-name').text(dictionaryFilename);
}
