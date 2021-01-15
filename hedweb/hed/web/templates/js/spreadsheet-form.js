const EXCEL_FILE_EXTENSIONS = ['xlsx', 'xls'];
const TEXT_FILE_EXTENSIONS = ['tsv', 'txt'];

$(function () {
    prepareSpreadsheetForm();
});


/**
 * Spreadsheet event handler function. Checks if the file uploaded has a valid spreadsheet extension.
 */
$('#spreadsheet-file').on('change', function () {
    let spreadsheet = $('#spreadsheet-file');
    let spreadsheetPath = spreadsheet.val();
    let spreadsheetFile = spreadsheet[0].files[0];
    resetFlashMessages();
    if (cancelWasPressedInChromeFileUpload(spreadsheetPath)) {
        resetForm();
    }
    else if (fileHasValidExtension(spreadsheetPath, EXCEL_FILE_EXTENSIONS)) {
        updateSpreadsheetFileLabel(spreadsheetPath);
        getWorksheetsInfo(spreadsheetFile);
    }
    else if (fileHasValidExtension(spreadsheetPath, TEXT_FILE_EXTENSIONS)) {
        updateSpreadsheetFileLabel(spreadsheetPath);
        clearWorksheetSelectbox();
        getColumnsInfo(spreadsheetFile, '');
    } else {
        resetForm();
        flashMessageOnScreen('Please upload a excel or text spreadsheet (.xlsx, .xls, .tsv, .txt)',
            'error', 'spreadsheet-flash');
    }
});

/**
 * Submits the form if the tag columns textbox is valid.
 */
$('#spreadsheet-validation-submit').on('click', function () {
    if (spreadsheetIsSpecified() && tagColumnsTextboxIsValid() && hedSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});

/**
 * Gets the information associated with the Excel worksheet that was newly selected. This information contains
 * the names of the columns and column indices that contain HED tags.
 */
$('#worksheet-name').on('change', function () {
    let spreadsheetFile = $('#spreadsheet-file')[0].files[0];
    let worksheetName = $('#worksheet-name option:selected').text();
    resetFlashMessages();
    getColumnsInfo(spreadsheetFile, worksheetName);
});

/**
 * Clears the spreadsheet file label.
 */
function clearSpreadsheetFileLabel() {
    $('#spreadsheet-display-name').text('');
}

/**
 * Clears tag column text boxes.
 */
function clearTagColumnTextboxes() {
    $('.textbox-group input[type="text"]').val('');
}

/**
 * Clears the worksheet select box.
 */
function clearWorksheetSelectbox() {
    $('#worksheet-name').empty();
}

/**
 * Checks to see if a dictionary is empty
 * @param {Array} dictionary - A dictionary
 * @returns {boolean} - True if the dictionary is empty. False, if otherwise.
 */
function dictionaryIsEmpty(dictionary) {
    return Object.keys(dictionary).length === 0;
}

/**
 * Flash a message showing the number of column columns that contain tags.
 * @param {Array} tagColumnIndices - An array of indices of columns containing tags
 * @param {Array} requiredTagColumnIndices - An array of indices of columns containing required tags
 * contain tags.
 */
function flashTagColumnCountMessage(tagColumnIndices, requiredTagColumnIndices) {
    let numberOfTagColumns = (tagColumnIndices.length + Object.keys(requiredTagColumnIndices).length).toString();
    if (numberOfTagColumns === '0') {
        flashMessageOnScreen('Warning: No tag column(s) found... Using the 2nd column', 'warning',
            'tag-columns-flash');
    } else {
        flashMessageOnScreen(numberOfTagColumns + ' tag column(s) found', 'success',
            'tag-columns-flash');
    }
}

/**
 * Flash a message showing the number of worksheets in an Excel workbook.
 * @param {Array} worksheetNames - An array containing the names of Excel workbook worksheets.
 */
function flashWorksheetNumberMessage(worksheetNames) {
    let numberOfWorksheets = worksheetNames.length.toString();
    flashMessageOnScreen(numberOfWorksheets + ' worksheet(s) found',
        'success', 'worksheet-flash');
}

/**
 * Gets the spreadsheet columns.
 * @param {Object} spreadsheetFile - A spreadsheet file.
 * @param {String} worksheetName - An Excel worksheet name.
 */
function getColumnsInfo(spreadsheetFile, worksheetName) {
    let formData = new FormData();
    formData.append('spreadsheet-file', spreadsheetFile);
    if (typeof worksheetName !== 'undefined') {
        formData.append('worksheet-name', worksheetName);
    }
    $.ajax({
        type: 'POST',
        url: "{{url_for('route_blueprint.get_spreadsheet_columns_info')}}",
        data: formData,
        contentType: false,
        processData: false,
        dataType: 'json',
        success: function (columnsInfo) {
            setComponentsRelatedToColumns(columnsInfo);
            flashTagColumnCountMessage(columnsInfo['tag-column-indices'],
                columnsInfo['required-tag-column-indices']);
        },
        error: function (jqXHR) {
            console.log(jqXHR.responseJSON.message);
            flashMessageOnScreen('Spreadsheet could not be processed.', 'error',
                'spreadsheet-flash');
        }
    });
}

/**
 * Gets information associated with the Excel workbook worksheets. This information contains the names of the
 * worksheets, the names of the columns in the first worksheet, and column indices that contain HED tags in the
 * first worksheet.
 * @param {Object} workbookFile - An Excel workbook file.
 */
function getWorksheetsInfo(workbookFile) {
    let formData = new FormData();
    formData.append('spreadsheet-file', workbookFile);
    $.ajax({
        type: 'POST',
        url: "{{url_for('route_blueprint.get_worksheets_info')}}",
        data: formData,
        contentType: false,
        processData: false,
        dataType: 'json',
        success: function (worksheetsInfo) {
            populateWorksheetSelectbox(worksheetsInfo['worksheet-names']);
            setComponentsRelatedToColumns(worksheetsInfo);
            flashWorksheetNumberMessage(worksheetsInfo['worksheet-names']);
            flashTagColumnCountMessage(worksheetsInfo['tag-column-indices'],
                worksheetsInfo['required-tag-column-indices']);
        },
        error: function (jqXHR) {
            console.log(jqXHR);
            // console.log(jqXHR.responseJSON.message);
            flashMessageOnScreen('Spreadsheet could not be processed.', 'error',
                'spreadsheet-validation-submit-flash');
        }
    });
}

/**
 * Hides  columns section in the form.
 */
function hideColumnNamesTable() {
    $('#column-names').hide();
}


/**
 * Populates a table containing the worksheet columns.
 * @param {Array} columnNames - An array containing the spreadsheet column names.
 */
function populateColumnNamesTable(columnNames) {
    let columnNamesTable = $('#columns-names-table');
    let columnNamesRow = $('<tr/>');
    let numberOfColumnNames = columnNames.length;
    columnNamesTable.empty();
    for (let i = 0; i < numberOfColumnNames; i++) {
        columnNamesRow.append('<td>' + columnNames[i] + '</td>');
    }
    columnNamesTable.append(columnNamesRow);
}


/**
 * Populate the required tag column textboxes from the tag column indices found in the spreadsheet columns.
 * @param {object} requiredTagColumnIndices - A dictionary containing the required tag column indices found
 * in the spreadsheet. The keys are the column names and the values are the indices.
 */
function populateRequiredTagColumnTextboxes(requiredTagColumnIndices) {
    for (let key in requiredTagColumnIndices) {
        $('#' + key.toLowerCase() + '-column').val(requiredTagColumnIndices[key].toString());
    }
}

/**
 * Populate the tag column textbox from the tag column indices found in the spreadsheet columns.
 * @param {Array} tagColumnIndices - An integer array of tag column indices found in the spreadsheet
 * columns.
 */
function populateTagColumnsTextbox(tagColumnIndices) {
    $('#tag-columns').val(tagColumnIndices.sort().map(String));
}

/**
 * Populate the Excel worksheet select box.
 * @param {Array} worksheetNames - An array containing the Excel worksheet names.
 */
function populateWorksheetSelectbox(worksheetNames) {
    let worksheetSelectbox = $('#worksheet-name');
    let numberOfWorksheetNames = worksheetNames.length;
    worksheetSelectbox.empty();
    for (let i = 0; i < numberOfWorksheetNames; i++) {
        worksheetSelectbox.append(new Option(worksheetNames[i], worksheetNames[i]));
    }
}

/**
 * Prepare the validation form after the page is ready. The form will be reset to handle page refresh and
 * components will be hidden and populated.
 */
function prepareSpreadsheetForm() {
    resetForm();
    getHEDVersions()
    hideColumnNamesTable();
    hideOtherHEDVersionFileUpload();
}

/**
 * Resets the flash messages that aren't related to the form submission.
 */
function resetFlashMessages() {
    flashMessageOnScreen('', 'success', 'spreadsheet-flash');
    flashMessageOnScreen('', 'success', 'worksheet-flash');
    flashMessageOnScreen('', 'success', 'tag-columns-flash');
    flashMessageOnScreen('', 'success', 'hed-flash');
    flashMessageOnScreen('', 'success', 'spreadsheet-validation-submit-flash');
}

/**
 * Resets the fields in the form.
 */
function resetForm() {
    $('#spreadsheet-form')[0].reset();
    clearSpreadsheetFileLabel();
    clearWorksheetSelectbox();
    hideColumnNamesTable();
    hideOtherHEDVersionFileUpload()
}

/**
 * Sets the components related to Excel worksheet columns when they are all empty.
 */
function setComponentsRelatedToEmptyColumnNames() {
    clearTagColumnTextboxes();
    setHasColumnNamesCheckboxToFalse();
    hideColumnNamesTable();
}

/**
 * Sets the components related to the spreadsheet tag column indices when they are empty.
 */
function setComponentsRelatedToEmptyTagColumnIndices() {
    $('#tag-columns').val('2');
}

/**
 * Sets the components related to the spreadsheet columns when they are not empty.
 * @param {Array} columnNames - An array containing the spreadsheet column names.
 */
function setComponentsRelatedToNonEmptyColumnNames(columnNames) {
    populateColumnNamesTable(columnNames);
    setHasColumnNamesCheckboxToTrue();
    $('#column-names').show();
}

/**
 * Sets the components related to the Excel worksheet columns.
 * @param {JSON} columnsInfo - A JSON object containing information related to the spreadsheet
 * columns.
 * This information contains the names of the columns and column indices that contain HED tags.
 */
function setComponentsRelatedToColumns(columnsInfo) {
    clearTagColumnTextboxes();
    if (columnNamesAreEmpty(columnsInfo['column-names'])) {
        setComponentsRelatedToEmptyColumnNames();
    } else {
        setComponentsRelatedToNonEmptyColumnNames(columnsInfo['column-names']);
    }
    if (tagColumnsIndicesAreEmpty(columnsInfo['tag-column-indices'])) {
        setComponentsRelatedToEmptyTagColumnIndices();
    } else {
        populateTagColumnsTextbox(columnsInfo['tag-column-indices']);
    }
    if (!dictionaryIsEmpty(columnsInfo['required-tag-column-indices'])) {
        populateRequiredTagColumnTextboxes(columnsInfo['required-tag-column-indices']);
    }
}

/**
 * Sets the spreadsheet has column names checkbox to false.
 */
function setHasColumnNamesCheckboxToFalse() {
    $('#has-column-names').prop('checked', false);
}

/**
 * Sets the spreadsheet has column names checkbox to true.
 */
function setHasColumnNamesCheckboxToTrue() {
    $('#has-column-names').prop('checked', true);
}

/**
 * Checks to see if the spreadsheet columns are empty.
 * @param {Array} columnNames - An array containing the spreadsheet column names.
 * @returns {boolean} - True if the spreadsheet columns are all empty.
 */
function columnNamesAreEmpty(columnNames) {
    let numberOfColumnNames = columnNames.length;
    for (let i = 0; i < numberOfColumnNames; i++) {
        if (!isEmptyStr(columnNames[i].trim())) {
            return false;
        }
    }
    return true;
}

/**
 * Checks to see if a spreadsheet has been specified.
 */
function spreadsheetIsSpecified() {
    let spreadsheetFile = $('#spreadsheet-file');
    if (spreadsheetFile[0].files.length === 0) {
        flashMessageOnScreen('Spreadsheet is not specified.', 'error',
            'spreadsheet-flash');
        return false;
    }
    return true;
}

/**
 * Checks to see if the worksheet tag column indices are empty.
 * @param {Array} tagColumnsIndices - An array containing the tag column indices based on the
 *                columns found in the spreadsheet.
 * @returns {boolean} - True if the spreadsheet tag column indices array is empty.
 */
function tagColumnsIndicesAreEmpty(tagColumnsIndices) {
    if (tagColumnsIndices.length > 0) {
        return false;
    }
    return true;
}

/**
 * Submit the form and return the validation results. If there are issues then they are returned in an attachment
 * file.
 */
function submitForm() {
    let spreadsheetForm = document.getElementById("spreadsheet-form");
    let formData = new FormData(spreadsheetForm);
    let worksheetName = $('#worksheet-name option:selected').text();
    let prefix = 'validation_issues';
    if(worksheetName) {
        prefix = prefix + '_worksheet_' + worksheetName;
    }
    let spreadsheetFile = $('#spreadsheet-file')[0].files[0].name;
    let display_name = convertToResultsName(spreadsheetFile, prefix)
    resetFlashMessages();
    flashMessageOnScreen('Worksheet is being validated ...', 'success',
        'spreadsheet-validation-submit-flash')
    $.ajax({
            type: 'POST',
            url: "{{url_for('route_blueprint.get_spreadsheet_validation_results')}}",
            data: formData,
            contentType: false,
            processData: false,
            dataType: 'text',
            success: function (downloaded_file) {
                  if (downloaded_file) {
                      flashMessageOnScreen('', 'success',
                          'spreadsheet-validation-submit-flash');
                      triggerDownloadBlob(downloaded_file, display_name);
                  } else {
                      flashMessageOnScreen('No validation errors found.', 'success',
                          'spreadsheet-validation-submit-flash');
                  }
            },
            error: function (download_response) {
                console.log(download_response.responseText);
                if (download_response.responseText.length < 100) {
                    flashMessageOnScreen(download_response.responseText, 'error',
                        'spreadsheet-validation-submit-flash');
                } else {
                    flashMessageOnScreen('Spreadsheet could not be processed',
                        'error','spreadsheet-validation-submit-flash');
                }
            }
        }
    )
    ;
}

/**
 * Checks to see if the tag columns textbox has valid input. Valid input is an integer or a comma-separated list of
 * integers that are the column indices in a Excel worksheet that contain HED tags.
 * @returns {boolean} - True if the tags columns textbox is valid.
 */
function tagColumnsTextboxIsValid() {
    let otherTagColumns = $('#tag-columns').val().trim();
    let valid = true;
    if (!isEmptyStr(otherTagColumns)) {
        let pattern = new RegExp('^([ \\d]+,)*[ \\d]+$');
        let valid = pattern.test(otherTagColumns);
        if (!valid) {
            flashMessageOnScreen('Tag column(s) must be a number or a comma-separated list of numbers',
                'error', 'tag-columns-flash')
        }
    }
    return valid;
}

/**
 * Updates the spreadsheet file label.
 * @param {String} spreadsheetPath - The path to the spreadsheet.
 */
function updateSpreadsheetFileLabel(spreadsheetPath) {
    let spreadsheetFilename = spreadsheetPath.split('\\').pop();
    $('#spreadsheet-display-name').text(spreadsheetFilename);
}
