from flask import current_app
from werkzeug import Response
from hed.schema.hed_schema_file import load_schema
from hed.util.error_reporter import get_printable_issue_string
from hed.util.hed_string import HedString
from hed.util.exceptions import HedFileError
from hed.validator.hed_validator import HedValidator
from hedweb.constants import common
from hedweb.web_utils import form_has_option, get_hed_path_from_pull_down, \
    generate_response_download_file_from_text, generate_text_response
app_config = current_app.config


def generate_input_from_hedstring_form(request):
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
    arguments = {common.COMMAND: '',
                 common.HED_XML_FILE: hed_file_path,
                 common.HED_DISPLAY_NAME: hed_display_name,
                 common.HEDSTRING: request.form['hedstring-input']}
    if form_has_option(request, common.HED_OPTION, common.HED_OPTION_VALIDATE):
        arguments[common.COMMAND] = common.COMMAND_VALIDATE
    elif form_has_option(request, common.HED_OPTION, common.HED_OPTION_TO_SHORT):
        arguments[common.COMMAND] = common.COMMAND_TO_SHORT
    elif form_has_option(request, common.HED_OPTION, common.HED_OPTION_TO_LONG):
        arguments[common.COMMAND] = common.COMMAND_TO_LONG

    return arguments


def hedstring_process(arguments):
    """Perform the requested action on the HED string.

    Parameters
    ----------
    arguments: dict
        A dictionary with the input arguments from the hedstring form

    Returns
    -------
    Response
        Downloadable response object.
    """

    if not arguments.get(common.HEDSTRING, None):
        raise HedFileError('EmptyHEDString', "Please enter a nonempty HED string to process", "")
    if arguments[common.COMMAND] == common.COMMAND_VALIDATE:
        return hedstring_validate(arguments)
    elif arguments[common.COMMAND] == common.COMMAND_TO_SHORT:
        return hedstring_convert(arguments)
    elif arguments[common.COMMAND] == common.COMMAND_TO_LONG:
        return hedstring_convert(arguments)
    else:
        raise HedFileError('UnknownProcessingMethod', "Select a hedstring processing method", "")


def hedstring_convert(arguments, hed_schema=None):
    """Converts a hedstring from short to long unless short_to_long is set to False, then long_to_short

    Parameters
    ----------
    arguments: dict
        Dictionary containing standard input form arguments
    hed_schema: HedSchema object

    Returns
    -------
    dict
        A dictionary with hedstring-results as the key
    """

    if not hed_schema:
        hed_schema = load_schema(arguments.get(common.HED_XML_FILE, ''))
    hed_string_obj = HedString(arguments.get(common.HEDSTRING))
    results = hedstring_validate(arguments, hed_schema)
    if results['msg_category'] == 'warning':
        return results
    if arguments[common.COMMAND] == common.TO_LONG:
        issues = hed_string_obj.convert_to_long(hed_schema)
    else:
        issues = hed_string_obj.convert_to_short(hed_schema)

    if issues:
        issues_str = get_printable_issue_string(issues, 'HED validation errors:')
        return {'data': issues_str, 'msg_category': 'warning', 'msg': 'String had validation errors, unable to convert'}
    else:
        return {'data': str(hed_string_obj), 'msg_category': 'success', 'msg': 'String conversion successful'}


def hedstring_validate(arguments, hed_schema=None):
    """Validates a hedstring and returns a dictionary containing the issues or a no errors message

    Parameters
    ----------
    arguments: dict
        Dictionary containing standard input form arguments
    hed_schema: str or HedSchema
        Version number or path or HedSchema object to be used

    Returns
    -------
    dict
        A dictionary with hedstring-results as the key
    """

    if not hed_schema:
        hed_schema = load_schema(arguments.get(common.HED_XML_FILE, ''))
    hed_validator = HedValidator(hed_schema=hed_schema)
    issues = hed_validator.validate_input(arguments.get(common.HEDSTRING))

    if issues:
        issues_str = get_printable_issue_string(issues, 'HED validation errors:')
        return {'data': issues_str, 'msg_category': 'warning', 'msg': 'String had validation errors'}
    else:
        return {'msg_category': 'success', 'msg': 'No validation errors found...'}
