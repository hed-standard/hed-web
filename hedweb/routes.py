from flask import render_template, request, Blueprint, current_app
from werkzeug.utils import secure_filename
import json

from hed import schema as hedschema

from hedweb.constants import base_constants, page_constants
from hedweb.constants import route_constants, file_constants
from hedweb.web_util import convert_hed_versions, get_parsed_name, handle_http_error, handle_error, package_results
from hedweb import sidecars as sidecar
from hedweb import events as events
from hedweb import spreadsheets as spreadsheets
from hedweb import services as services
from hedweb import strings as strings
from hedweb import schemas as schema
from hedweb.columns import get_columns_request

app_config = current_app.config
route_blueprint = Blueprint(route_constants.ROUTE_BLUEPRINT, __name__)


@route_blueprint.route(route_constants.COLUMNS_INFO_ROUTE, methods=['POST'])
def columns_info_results():
    """ Return spreadsheets column and sheet names.

    Returns:
        str: A serialized JSON string with column and sheet_name information.

    """
    try:
        columns_info = get_columns_request(request)
        return json.dumps(columns_info)
    except Exception as ex:
        return handle_error(ex)


@route_blueprint.route(route_constants.EVENTS_SUBMIT_ROUTE, strict_slashes=False, methods=['POST'])
def events_results():
    """ Process events form submission and return results.

    Returns:
        Response: The response appropriate to the request.

    Notes:
        The response depends on the request:
        - validation: text file with validation errors
        - assemble:  an assembled events file containing assembled events.
        - generate:  a JSON sidecar generated from the events file.

    """

    try:
        input_arguments = events.get_events_form_input(request)
        a = events.process(input_arguments)
        return package_results(a)
    except Exception as ex:
        return handle_http_error(ex)


@route_blueprint.route(route_constants.SCHEMAS_SUBMIT_ROUTE, strict_slashes=False, methods=['POST'])
def schemas_results():
    """ Process schema form submission and return results.

    Returns:
        Response: The response appropriate to the request.

    Notes:
        The response depends on the request:
        - validation: text file with validation errors
        - convert:  text file with converted schema.

    """
    try:
        arguments = schema.get_input_from_form(request)
        a = schema.process(arguments)
        return package_results(a)
    except Exception as ex:
        return handle_http_error(ex)


@route_blueprint.route(route_constants.SCHEMA_VERSION_ROUTE, methods=['POST'])
def schema_version_results():
    """ Return the version of the schema as a JSON string.

    Returns:
        string: A serialized JSON string containing the version of the schema.

    """

    try:
        hed_info = {}
        if base_constants.SCHEMA_PATH in request.files:
            f = request.files[base_constants.SCHEMA_PATH]
            name, extension = get_parsed_name(secure_filename(f.filename))
            hed_schema = hedschema.from_string(f.stream.read(file_constants.BYTE_LIMIT).decode('ascii'),
                                               schema_format=extension)
            hed_info[base_constants.SCHEMA_VERSION] = hed_schema.get_formatted_version()
        return json.dumps(hed_info)
    except Exception as ex:
        return handle_error(ex)


@route_blueprint.route(route_constants.SCHEMA_VERSIONS_ROUTE, methods=['GET', 'POST'])
def schema_versions_results():
    """ Return serialized JSON string with hed versions.

    Returns:
        str: A serialized JSON string containing a list of the HED versions.

    """

    try:
        hedschema.cache_xml_versions()
        hed_info = {base_constants.SCHEMA_VERSION_LIST: hedschema.get_hed_versions(library_name="all")}
        hed_list = convert_hed_versions(hed_info)
        return json.dumps(hed_list)
    except Exception as ex:
        return handle_error(ex)


@route_blueprint.route(route_constants.SERVICES_SUBMIT_ROUTE, strict_slashes=False, methods=['POST'])
def services_results():
    """ Perform the requested web service and return the results in JSON.

    Returns:
        str: A serialized JSON string containing processed information.

    """

    try:
        hedschema.set_cache_directory(current_app.config['HED_CACHE_FOLDER'])
        hedschema.cache_xml_versions()
        arguments = services.get_input_from_request(request)
        response = services.process(arguments)
        return json.dumps(response)
    except Exception as ex:
        errors = handle_error(ex, return_as_str=False)
        response = {'error_type': errors.get('error_type', 'Unknown error type'),
                    'error_msg': errors.get('message', 'Unknown failure')}
        return json.dumps(response)


@route_blueprint.route(route_constants.SIDECARS_SUBMIT_ROUTE, strict_slashes=False, methods=['POST'])
def sidecars_results():
    """ Process sidecar form submission and return results.

    Returns:
        Response: The response appropriate to the request.

    Notes:
        The response depends on the request:
        - validation: text file with validation errors
        - convert:  converted sidecar.
        - extract:  4-column spreadsheets.
        - merge:  a merged sidecar.

    """

    try:
        input_arguments = sidecar.get_input_from_form(request)
        a = sidecar.process(input_arguments)
        b = package_results(a)
        return b
        # return package_results(a)
    except Exception as ex:
        return handle_http_error(ex)


@route_blueprint.route(route_constants.SPREADSHEETS_SUBMIT_ROUTE, strict_slashes=False, methods=['POST'])
def spreadsheets_results():
    """ Process the spreadsheets in the form and return results.

    Returns:
        Response: The response appropriate to the request.

    Notes:
        The response depends on the request:
        - validation: text file with validation errors
        - convert:  converted spreadsheets.

    """

    try:
        arguments = spreadsheets.get_input_from_form(request)
        a = spreadsheets.process(arguments)
        response = package_results(a)
        return response
    except Exception as ex:
        return handle_http_error(ex)


@route_blueprint.route(route_constants.STRINGS_SUBMIT_ROUTE, strict_slashes=False, methods=['GET', 'POST'])
def strings_results():
    """ Process string entered in a form text box.

    Returns:
        Response: The response appropriate to the request.

    Notes:
        The response depends on the request, but appears in text box.
        - validation: validation errors
        - convert:  converted sting.

    """
    try:
        input_arguments = strings.get_input_from_form(request)
        a = strings.process(input_arguments)
        return json.dumps(a)
    except Exception as ex:
        return handle_error(ex)


@route_blueprint.route(route_constants.EVENTS_ROUTE, strict_slashes=False, methods=['GET'])
def render_events_form():
    """ Form for BIDS event file (with JSON sidecar) processing.

    Returns:
        template: A rendered template for the events form.

    """
    ver = app_config['VERSIONS']
    return render_template(page_constants.EVENTS_PAGE,
                           tool_ver=ver["tool_ver"], tool_date=ver["tool_date"],
                           web_ver=ver["web_ver"], web_date=ver["web_date"])


@route_blueprint.route(route_constants.HED_TOOLS_HOME_ROUTE, strict_slashes=False, methods=['GET'])
def render_home_page():
    """ The home page.

    Returns:
        template: A rendered template for the home page.

    """
    ver = app_config['VERSIONS']
    return render_template(page_constants.HED_TOOLS_HOME_PAGE,
                           tool_ver=ver["tool_ver"], tool_date=ver["tool_date"],
                           web_ver=ver["web_ver"], web_date=ver["web_date"])


@route_blueprint.route(route_constants.SCHEMAS_ROUTE, strict_slashes=False, methods=['GET'])
def render_schemas_form():
    """ The schema processing form.

    Returns:
        template: A rendered template for the schema processing form.

    """
    ver = app_config['VERSIONS']
    return render_template(page_constants.SCHEMAS_PAGE,
                           tool_ver=ver["tool_ver"], tool_date=ver["tool_date"],
                           web_ver=ver["web_ver"], web_date=ver["web_date"])


@route_blueprint.route(route_constants.SERVICES_ROUTE, strict_slashes=False, methods=['GET'])
def render_services_form():
    """ Landing page for HED hedweb services.

    Returns:
        template: A dummy rendered template so that the service can get a csrf token.

    """
    ver = app_config['VERSIONS']
    return render_template(page_constants.SERVICES_PAGE,
                           tool_ver=ver["tool_ver"], tool_date=ver["tool_date"],
                           web_ver=ver["web_ver"], web_date=ver["web_date"])


@route_blueprint.route(route_constants.SIDECARS_ROUTE, strict_slashes=False, methods=['GET'])
def render_sidecars_form():
    """ The sidecar form.

    Returns:
        template: A rendered template for the sidecar form.

    """
    ver = app_config['VERSIONS']
    return render_template(page_constants.SIDECARS_PAGE,
                           tool_ver=ver["tool_ver"], tool_date=ver["tool_date"],
                           web_ver=ver["web_ver"], web_date=ver["web_date"])


@route_blueprint.route(route_constants.SPREADSHEETS_ROUTE, strict_slashes=False, methods=['GET'])
def render_spreadsheets_form():
    """ The spreadsheets form.

    Returns:
        template: A rendered template for the spreadsheets form.

    """
    ver = app_config['VERSIONS']
    return render_template(page_constants.SPREADSHEETS_PAGE,
                           tool_ver=ver["tool_ver"], tool_date=ver["tool_date"],
                           web_ver=ver["web_ver"], web_date=ver["web_date"])


@route_blueprint.route(route_constants.STRINGS_ROUTE, strict_slashes=False, methods=['GET'])
def render_strings_form():
    """ The HED string form.

    Returns:
        template: A rendered template for the HED string form.

    """
    ver = app_config['VERSIONS']
    return render_template(page_constants.STRINGS_PAGE,
                           tool_ver=ver["tool_ver"], tool_date=ver["tool_date"],
                           web_ver=ver["web_ver"], web_date=ver["web_date"])
