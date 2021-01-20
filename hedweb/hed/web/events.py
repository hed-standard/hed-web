
import os
from urllib.error import URLError, HTTPError
from flask import current_app
from werkzeug.utils import secure_filename

from hed.util.file_util import  delete_file_if_it_exist
from hed.validator.hed_validator import HedValidator
from hed.util.hed_file_input import HedFileInput

from hed.web.constants import common_constants, error_constants, file_constants
from hed.web import web_utils
from hed.web import utils

app_config = current_app.config


def generate_arguments_from_validation_form(form_request_object):
    """Gets the validation function input arguments from a request object associated with the validation form.

    Parameters
    ----------
    form_request_object: Request object
        A Request object containing user data from the validation form.

    Returns
    -------
    dictionary
        A dictionary containing input arguments for calling the underlying validation function.
    """
    hed_file_path, hed_display_name = web_utils.get_hed_path_from_pull_down(form_request_object)
    uploaded_file_name, original_file_name = \
        web_utils.get_uploaded_file_path_from_form(form_request_object, common_constants.SPREADSHEET_FILE,
                                                   file_constants.SPREADSHEET_FILE_EXTENSIONS)

    validation_input_arguments = {common_constants.HED_XML_FILE: hed_file_path,
                                  common_constants.HED_DISPLAY_NAME: hed_display_name,
                                  common_constants.SPREADSHEET_PATH: uploaded_file_name,
                                  common_constants.SPREADSHEET_FILE: original_file_name}

    validation_input_arguments[common_constants.WORKSHEET_NAME] = \
        utils.get_optional_form_field(form_request_object, common_constants.WORKSHEET_NAME,
                                      common_constants.STRING)
    validation_input_arguments[common_constants.HAS_COLUMN_NAMES] = utils.get_optional_form_field(
        form_request_object, common_constants.HAS_COLUMN_NAMES, common_constants.BOOLEAN)
    validation_input_arguments[common_constants.CHECK_FOR_WARNINGS] = utils.get_optional_form_field(
        form_request_object, common_constants.CHECK_FOR_WARNINGS, common_constants.BOOLEAN)
    return validation_input_arguments


def generate_spreadsheet_validation_filename(spreadsheet_filename, worksheet_name=''):
    """Generates a filename for the attachment that will contain the spreadsheet validation issues.

    Parameters
    ----------
    spreadsheet_filename: string
        The name of the spreadsheet other.
    worksheet_name: string
        The name of the spreadsheet worksheet.
    Returns
    -------
    string
        The name of the attachment other containing the validation issues.
    """
    if worksheet_name:
        return common_constants.VALIDATION_OUTPUT_FILE_PREFIX + \
               secure_filename(spreadsheet_filename).rsplit('.')[0] + '_' + \
               secure_filename(worksheet_name) + file_constants.TEXT_EXTENSION
    return common_constants.VALIDATION_OUTPUT_FILE_PREFIX + secure_filename(spreadsheet_filename).rsplit('.')[
        0] + file_constants.TEXT_EXTENSION


def report_events_validation_status(form_request_object):
    """Reports the spreadsheet validation status.

    Parameters
    ----------
    form_request_object: Request object
        A Request object containing user data from the validation form.

    Returns
    -------
    string
        A serialized JSON string containing information related to the worksheet columns. If the validation fails then a
        500 error message is returned.
    """
    input_arguments = []
    try:
        input_arguments = generate_arguments_from_validation_form(form_request_object)
        hed_validator = validate_spreadsheet(input_arguments)
        validation_issues = hed_validator.get_validation_issues()
        if validation_issues:
            issues_filename = web_utils.generate_issues_filename(common_constants.VALIDATION_OUTPUT_FILE_PREFIX,
                                                                 input_arguments[common_constants.SPREADSHEET_FILE],
                                                                 input_arguments[common_constants.WORKSHEET_NAME])

            issue_file = web_utils.save_issues_to_upload_folder(validation_issues, issues_filename)
            download_response = web_utils.generate_download_file_response(issue_file)
            if isinstance(download_response, str):
                return web_utils.handle_http_error(error_constants.NOT_FOUND_ERROR, download_response)
            return download_response
    except HTTPError:
        return error_constants.NO_URL_CONNECTION_ERROR
    except URLError:
        return error_constants.INVALID_URL_ERROR
    except Exception as e:
        return "Unexpected processing error: " + str(e)
    finally:
        delete_file_if_it_exist(input_arguments[common_constants.SPREADSHEET_PATH])
        # delete_file_if_it_exist(input_arguments[common_constants.HED_XML_FILE])
    return ""


def validate_spreadsheet(validation_arguments):
    """Validates the spreadsheet.

    Parameters
    ----------
    validation_arguments: dictionary
        A dictionary containing the arguments for the validation function.

    Returns
    -------
    HedValidator object
        A HedValidator object containing the validation results.
    """

    file_input_object = HedFileInput(validation_arguments[common_constants.SPREADSHEET_PATH],
                                     worksheet_name=validation_arguments[common_constants.WORKSHEET_NAME],
                                     has_column_names=validation_arguments[common_constants.HAS_COLUMN_NAMES])

    return HedValidator(file_input_object,
                        check_for_warnings=validation_arguments[common_constants.CHECK_FOR_WARNINGS],
                        hed_xml_file=validation_arguments[common_constants.HED_XML_FILE])
