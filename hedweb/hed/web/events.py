
from urllib.error import URLError, HTTPError
from flask import current_app

from hed.schema.hed_schema_file import load_schema
from hed.util.file_util import delete_file_if_it_exists
from hed.util.exceptions import HedFileError
from hed.validator.hed_validator import HedValidator
from hed.web.constants import common_constants, error_constants, file_constants
from hed.web.dictionary import validate_dictionary_new, validate_dictionary
from hed.web.spreadsheet import validate_spreadsheet
from hed.web.web_utils import get_hed_path_from_pull_down, get_uploaded_file_path_from_form, get_optional_form_field

app_config = current_app.config


def generate_input_from_events_form(request):
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
    uploaded_events_name, original_events_name = \
        get_uploaded_file_path_from_form(request, common_constants.SPREADSHEET_FILE,
                                         file_constants.SPREADSHEET_FILE_EXTENSIONS)

    uploaded_json_name, original_json_name = \
        get_uploaded_file_path_from_form(request, common_constants.JSON_FILE,
                                         file_constants.DICTIONARY_FILE_EXTENSIONS)

    input_arguments = {
        common_constants.HED_XML_FILE: hed_file_path,
        common_constants.HED_DISPLAY_NAME: hed_display_name,
        common_constants.SPREADSHEET_PATH: uploaded_events_name,
        common_constants.SPREADSHEET_FILE: original_events_name,
        common_constants.JSON_PATH: uploaded_json_name,
        common_constants.JSON_FILE: original_json_name,
        common_constants.WORKSHEET_NAME: get_optional_form_field(request, common_constants.WORKSHEET_NAME,
                                                                 common_constants.STRING),
        common_constants.HAS_COLUMN_NAMES: get_optional_form_field(request,
                                                                   common_constants.HAS_COLUMN_NAMES,
                                                                   common_constants.BOOLEAN),
        common_constants.CHECK_FOR_WARNINGS: get_optional_form_field(request,
                                                                     common_constants.CHECK_FOR_WARNINGS,
                                                                     common_constants.BOOLEAN)
    }
    return input_arguments


def report_events_validation_status(input_arguments):
    """Reports the spreadsheet validation status.

    Parameters
    ----------
    input_arguments: dict
        A dictionary of the values extracted from the form

    Returns
    -------
    Response
         The validation results as a Response object
    """

    hed_schema = load_schema(input_arguments.get(common_constants.HED_XML_FILE, ''))
    download_response = validate_dictionary_new(input_arguments, hed_schema=hed_schema)
    if not hasattr(download_response, 'headers'):
        raise HedFileError('DictionaryNotValidated',
                           'Dictionary could not be validated so event validation incomplete', '')
    response = getattr(download_response, 'response')
    headers = getattr(download_response, 'headers')
    if headers.getlist('Content-Disposition'):
        return download_response
    if headers.getlist('Content-Length') and int(headers.getlist('Content-Length')[0]) > 0:
        return download_response
    hed_validator = HedValidator(hed_schema=hed_schema,
                                 check_for_warnings=input_arguments.get(common_constants.CHECK_FOR_WARNINGS, False))
    return validate_spreadsheet(input_arguments, hed_validator)
