from urllib.error import URLError
from flask import current_app

from hed.util.error_reporter import get_printable_issue_string
from hed.validator.hed_validator import HedValidator
from hed.util.hed_file_input import HedFileInput

import hed.web.web_utils
from hed.web.constants import common, file_constants, spreadsheet_constants
from hed.web.web_utils import convert_number_str_to_list, generate_filename, \
    generate_download_file_response, get_hed_path_from_pull_down, get_uploaded_file_path_from_form, \
    get_optional_form_field, save_text_to_upload_folder, generate_text_response
from hed.web import spreadsheet_utils

app_config = current_app.config


def get_specific_tag_columns_from_form(request):
    """Gets the specific tag columns from the validation form.

    Parameters
    ----------
    request: Request object
        A Request object containing user data from the validation form.

    Returns
    -------
    dictionary
        A dictionary containing the required tag columns. The keys will be the column numbers and the values will be
        the name of the column.
    """
    column_prefix_dictionary = {}
    for tag_column_name in spreadsheet_constants.SPECIFIC_TAG_COLUMN_NAMES:
        form_tag_column_name = tag_column_name.lower() + common.COLUMN_POSTFIX
        if form_tag_column_name in request.form:
            tag_column_name_index = request.form[form_tag_column_name].strip()
            if tag_column_name_index:
                tag_column_name_index = int(tag_column_name_index)

                # todo: Remove these giant kludges at some point
                if tag_column_name == "Long":
                    tag_column_name = "Long Name"
                tag_column_name = "Event/" + tag_column_name + "/"
                # End giant kludges

                column_prefix_dictionary[tag_column_name_index] = tag_column_name
    return column_prefix_dictionary


def generate_input_from_spreadsheet_form(request):
    """Gets the validation function input arguments from a request object associated with the validation form.

    Parameters
    ----------
    request: Request object
        A Request object containing user data from the validation form.

    Returns
    -------
    dictionary
        A dictionary containing input arguments for calling the underlying validation function.
    """
    hed_file_path, hed_display_name = get_hed_path_from_pull_down(request)
    uploaded_file_name, original_file_name = \
        get_uploaded_file_path_from_form(request, common.SPREADSHEET_FILE, file_constants.SPREADSHEET_FILE_EXTENSIONS)

    input_arguments = {
        common.HED_XML_FILE: hed_file_path,
        common.HED_DISPLAY_NAME: hed_display_name,
        common.SPREADSHEET_PATH: uploaded_file_name,
        common.SPREADSHEET_FILE: original_file_name,
        common.TAG_COLUMNS: convert_number_str_to_list(request.form[common.TAG_COLUMNS]),
        common.COLUMN_PREFIX_DICTIONARY: get_specific_tag_columns_from_form(request),
        common.WORKSHEET_NAME: get_optional_form_field(request, common.WORKSHEET_NAME, common.STRING),
        common.HAS_COLUMN_NAMES: get_optional_form_field(request, common.HAS_COLUMN_NAMES, common.BOOLEAN),
        common.CHECK_FOR_WARNINGS: get_optional_form_field(request, common.CHECK_FOR_WARNINGS, common.BOOLEAN)
    }
    return input_arguments


def validate_spreadsheet(input_arguments, hed_validator=None):
    """Validates the spreadsheet.

    Parameters
    ----------
    input_arguments: dictionary
        A dictionary containing the arguments for the validation function.
    hed_validator: HedValidator
        Validator passed if previously created in another phase
    Returns
    -------
    HedValidator object
        A HedValidator object containing the validation results.
    """

    file_input = HedFileInput(input_arguments.get(common.SPREADSHEET_PATH, None),
                              worksheet_name=input_arguments.get(common.WORKSHEET_NAME, None),
                              tag_columns=input_arguments.get(common.TAG_COLUMNS, None),
                              has_column_names=input_arguments.get(common.HAS_COLUMN_NAMES, None),
                              column_prefix_dictionary=input_arguments.get(common.COLUMN_PREFIX_DICTIONARY,
                                                                           None))
    if not hed_validator:
        hed_validator = HedValidator(hed_xml_file=input_arguments.get(common.HED_XML_FILE, ''),
                                     check_for_warnings=input_arguments.get(common.CHECK_FOR_WARNINGS, False))

    issues = hed_validator.validate_input(file_input)

    if issues:
        display_name = input_arguments.get(common.SPREADSHEET_FILE, None)
        worksheet_name = input_arguments.get(common.WORKSHEET_NAME, None)
        title_string = display_name
        suffix = 'validation_errors'
        if worksheet_name:
            title_string = display_name + ' [worksheet ' + worksheet_name + ']'
            suffix = '_worksheet_' + worksheet_name + '_' + suffix
        issue_str = get_printable_issue_string(issues, f"{title_string} HED validation errors")

        file_name = generate_filename(display_name, suffix=suffix, extension='.txt')
        issue_file = save_text_to_upload_folder(issue_str, file_name)
        return generate_download_file_response(issue_file, display_name=file_name, category='warning',
                                               msg='Spreadsheet had validation errors')
    else:
        return generate_text_response("", msg='Spreadsheet had no validation errors')
