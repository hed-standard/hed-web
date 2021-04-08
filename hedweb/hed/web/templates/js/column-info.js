

/**
 * Clears tag column text boxes.
 */
function clearTagColumnTextboxes() {
    $('.textbox-group input[field_type="text"]').val('');
}

/**
 * Checks to see if any entries in an array of names are empty.
 * @param {Array} names - An array containing a list of names.
 * @returns {boolean} - True if any of the names in the array are all empty.
 */
function columnNamesAreEmpty(names) {
    if (names !== undefined) {
        let numberOfNames = names.length;
        for (let i = 0; i < numberOfNames; i++) {
            if (!isEmptyStr(names[i].trim())) {
                return false;
            }
        }
    }
    return true;
}

/**
 * Gets the columns information from a spreadsheet-like data file
 * @param {string} formID - ID of the form that is from
 * @param {string} pathID - Form ID of the path of a spreadsheet-like file with column names.
 * @returns string or array
 */
function getColumnsInfo(formID, pathID) {
    let returnInfo = 'Oops'
    let form = document.getElementById(formID);
    let formData = new FormData(form);
    // formData.append('column-file-path', pathID)
    $.ajax({
        type: 'POST',
        url: "{{url_for('route_blueprint.get_columns_info_results')}}",
        data: formData,
        contentType: false,
        processData: false,
        dataType: 'text',
        success: function (columnsInfo) {
            returnInfo = columnsInfo;
        },
        error: function (jqXHR) {
            returnInfo = 'File column information processing failed.';
        }
    });
    return returnInfo;
}
/**
 * Hides  columns section in the form.
 */
function hideColumnNames() {
    $('#column-names').hide();
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
 * Populates a table containing one row.
 * @param {Array} columnNames - An array containing the spreadsheet column names.
 * @param {String} tableID - String containing the ID of the table
 */
function populateTableHeaders(columnNames, tableID) {
    let columnTable = $('#column-names-table');
    let columnNamesRow = $('<tr/>');
    let numberOfColumnNames = columnNames.length;
    columnTable.empty();
    for (let i = 0; i < numberOfColumnNames; i++) {
        columnNamesRow.append('<td>' + columnNames[i] + '</td>');
    }
    columnTable.append(columnNamesRow);
}

/**
 * Populate the tag column textbox from the tag column indices found in the spreadsheet columns.
 * @param {Array} tagColumnIndices - An integer array of tag column indices found in the spreadsheet
 * columns.
 */
function populateTagColumnsTextbox(tagColumnIndices) {
    $('#tag-columns').val(tagColumnIndices.sort().map(String));
}

/*
/!**
 * Sets the components related to the Excel worksheet columns.
 * @param {JSON} columnsInfo - A JSON object containing information related to the spreadsheet
 * columns.
 * This information contains the names of the columns and column indices that contain HED tags.
 *!/
function setComponentsRelatedToColumns(columnsInfo) {
    if (columnNamesAreEmpty(columnsInfo['column-names'])) {
        setComponentsRelatedToEmptyColumnNames();
    } else {
        setComponentsRelatedToNonEmptyColumnNames(columnsInfo['column-names']);
    }
}*/

/**
 * Sets the components related to the Excel worksheet columns.
 * @param {JSON} columnsInfo - A JSON object containing information related to the spreadsheet
 * columns.
 * This information contains the names of the columns and column indices that contain HED tags.
 */
function setComponentsRelatedToColumns(columnsInfo, showIndices = false) {
    clearTagColumnTextboxes();
    if (columnNamesAreEmpty(columnsInfo['column-names'])) {
        setComponentsRelatedToEmptyColumnNames();
    } else {
        setComponentsRelatedToNonEmptyColumnNames(columnsInfo['column-names']);
    }
    if (showIndices) {
        if (!tagColumnsIndicesAreEmpty(columnsInfo['tag-column-indices'])) {
            setComponentsRelatedToEmptyTagColumnIndices();
        } else {
            populateTagColumnsTextbox(columnsInfo['tag-column-indices']);
        }
        if (Object.keys(columnsInfo['required-tag-column-indices']).length !== 0) {
            populateRequiredTagColumnTextboxes(columnsInfo['required-tag-column-indices']);
        }
    }
}

/**
 * Sets the components related to Excel worksheet columns when they are all empty.
 */
function setComponentsRelatedToEmptyColumnNames() {
    clearTagColumnTextboxes();
    setHasColumnNamesCheckbox(false);
    hideColumnNames();
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
    showColumnNames(columnNames)
    setHasColumnNamesCheckbox(true);
}

/**
 * Sets the spreadsheet has column names checkbox to false.
 * @param {boolean} value - is checked if true and unchecked if false
 */
function setHasColumnNamesCheckbox(value) {
    $('#has-column-names').prop('checked', value);
}

/**
 * Sets the components related to the spreadsheet columns when they are not empty.
 * @param {Array} columnNames - An array containing the spreadsheet column names.
 */
function showColumnNames(columnNames) {
    populateTableHeaders(columnNames);
    $('#column-names').show();
}

/**
 * Checks to see if the worksheet tag column indices are empty.
 * @param {Array} tagColumnsIndices - An array containing the tag column indices based on the
 *                columns found in the spreadsheet.
 * @returns {boolean} - True if the spreadsheet tag column indices array is empty.
 */
function tagColumnsIndicesAreEmpty(tagColumnsIndices) {
    return tagColumnsIndices.length <= 0
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
